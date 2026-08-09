"""
FFHQ unseen 이미지 배치로 진단 신뢰성 파이프라인을 정량 평가합니다.

측정 지표:
  1. 모순율(self-contradiction rate) — 질환·상태 판정이 서로 논리적으로 어긋나는 비율
  2. 모델별 저신뢰 비율 — 타입/질환/상태 각각 confidence < 0.6 인 비율
  3. 안전 게이트 범위 좁히기 전/후 설명 가능 비율
     - 전(구): 타입 포함 어떤 모델이든 저신뢰면 차단 (uncertainty.is_uncertain)
     - 후(신): 질환·상태 관련 신호만 보고 차단 (grounded_explanation.available)

실행 방법 (skin_project 루트에서):
  python eval/run_contradiction_eval.py
"""
import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_model_service import skin_analysis_service

IMAGE_DIR = Path(__file__).parent / "images" / "unseen"
RESULTS_PATH = Path(__file__).parent / "results.json"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


async def analyze_all() -> list[dict]:
    if not skin_analysis_service.models_loaded:
        skin_analysis_service.load_models()

    image_paths = sorted(p for p in IMAGE_DIR.iterdir() if p.suffix.lower() in IMAGE_EXTS)
    if not image_paths:
        print(f"이미지가 없습니다: {IMAGE_DIR}")
        return []

    records = []
    for i, path in enumerate(image_paths, 1):
        result = await skin_analysis_service.analyze_skin_comprehensive(path.read_bytes())
        if not result.get("success"):
            print(f"[{i}/{len(image_paths)}] {path.name} — 분석 실패: {result.get('error')}")
            continue

        uncertainty = result["uncertainty"]
        grounded = result["grounded_explanation"]
        disease = result["skin_disease"]["disease"]
        state = result["skin_state"]["state"]
        has_finding = disease not in ("정상", "알 수 없음") or state not in ("양호", "알 수 없음")

        record = {
            "file": path.name,
            "skin_type": result["skin_type"]["type"],
            "type_conf": round(result["skin_type"]["confidence"], 3),
            "disease": disease,
            "disease_conf": round(result["skin_disease"]["confidence"], 3),
            "state": state,
            "state_conf": round(result["skin_state"]["confidence"], 3),
            "flags": uncertainty["flags"],
            "is_contradiction": any(f["type"] == "contradiction" for f in uncertainty["flags"]),
            "has_finding": has_finding,
            "old_gate_available": has_finding and not uncertainty["is_uncertain"],
            "new_gate_available": grounded.get("available", False),
        }
        records.append(record)
        print(f"[{i}/{len(image_paths)}] {path.name} -> 타입:{record['skin_type']}({record['type_conf']:.0%}) "
              f"질환:{disease}({record['disease_conf']:.0%}) 상태:{state}({record['state_conf']:.0%}) "
              f"모순:{record['is_contradiction']}")

    return records


def summarize(records: list[dict]) -> dict:
    n = len(records)
    if n == 0:
        return {}

    contradiction_rate = sum(r["is_contradiction"] for r in records) / n

    low_conf_count = {"피부 타입": 0, "피부 질환": 0, "피부 상태": 0}
    for r in records:
        for f in r["flags"]:
            if f["type"] == "low_confidence":
                low_conf_count[f["model"]] += 1
    low_conf_rate = {k: v / n for k, v in low_conf_count.items()}

    finding_records = [r for r in records if r["has_finding"]]
    m = len(finding_records)
    old_availability = sum(r["old_gate_available"] for r in finding_records) / m if m else None
    new_availability = sum(r["new_gate_available"] for r in finding_records) / m if m else None

    return {
        "total_images": n,
        "contradiction_rate": round(contradiction_rate, 3),
        "low_confidence_rate_by_model": {k: round(v, 3) for k, v in low_conf_rate.items()},
        "finding_cases": m,
        "explanation_availability_old_gate": round(old_availability, 3) if old_availability is not None else None,
        "explanation_availability_new_gate": round(new_availability, 3) if new_availability is not None else None,
    }


async def main():
    records = await analyze_all()
    if not records:
        return

    summary = summarize(records)

    RESULTS_PATH.write_text(
        json.dumps({"summary": summary, "records": records}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("\n" + "=" * 60)
    print(f"이미지 수: {summary['total_images']}")
    print(f"모순율: {summary['contradiction_rate']:.1%}")
    print("모델별 저신뢰 비율:")
    for model, rate in summary["low_confidence_rate_by_model"].items():
        print(f"  - {model}: {rate:.1%}")
    print(f"설명 대상 케이스: {summary['finding_cases']}건")
    if summary["explanation_availability_old_gate"] is not None:
        print(f"설명 가능 비율 (게이트 좁히기 전): {summary['explanation_availability_old_gate']:.1%}")
        print(f"설명 가능 비율 (게이트 좁히기 후): {summary['explanation_availability_new_gate']:.1%}")
    print(f"\n상세 결과 저장: {RESULTS_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
