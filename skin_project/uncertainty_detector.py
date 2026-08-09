"""
모델 출력 간 모순(Contradiction) 및 저신뢰(Low-confidence) 케이스를 감지합니다.

배경:
  질환 모델(YOLO)과 상태 모델(YOLO)은 독립적으로 추론하므로
  서로 논리적으로 맞지 않는 결과가 나올 수 있습니다.
  예) 질환="정상" + 상태="트러블"(고신뢰) → 불일치

판단 기준:
  - 저신뢰: 어떤 모델이든 confidence < 0.6
  - 모순: 질환="정상" + 상태(이상) confidence >= 0.7
"""

CONF_THRESHOLD = 0.6       # 저신뢰 임계값
CONTRADICTION_THRESHOLD = 0.7  # 모순 판정 임계값

# 상태 모델에서 "정상"으로 간주하는 클래스
NORMAL_STATES = {"양호"}


def detect_uncertainty(
    skin_type_result: dict,
    skin_disease_result: dict,
    skin_state_result: dict,
) -> dict:
    """
    세 모델 출력을 받아 불확실성 여부를 반환합니다.

    Returns:
        {
            "is_uncertain": bool,
            "reason": str,
            "flags": list[dict],
            "top_classes": dict
        }
    """
    flags = []

    disease = skin_disease_result.get("disease", "알 수 없음")
    disease_conf = skin_disease_result.get("confidence", 0.0)
    state = skin_state_result.get("state", "알 수 없음")
    state_conf = skin_state_result.get("confidence", 0.0)
    skin_type = skin_type_result.get("type", "알 수 없음")
    type_conf = skin_type_result.get("confidence", 0.0)

    # --- 저신뢰 감지 ---
    if type_conf < CONF_THRESHOLD:
        flags.append({
            "type": "low_confidence",
            "model": "피부 타입",
            "value": round(type_conf, 3),
        })

    # 정상 판정(탐지 없음)은 저신뢰 대상 제외
    if disease != "정상" and disease_conf < CONF_THRESHOLD:
        flags.append({
            "type": "low_confidence",
            "model": "피부 질환",
            "value": round(disease_conf, 3),
        })

    if state not in NORMAL_STATES and state_conf < CONF_THRESHOLD and state != "알 수 없음":
        flags.append({
            "type": "low_confidence",
            "model": "피부 상태",
            "value": round(state_conf, 3),
        })

    # --- 모순 감지 ---
    # 질환 모델은 정상이라 했지만, 상태 모델이 이상 상태를 고신뢰로 탐지
    if (
        disease == "정상"
        and state not in NORMAL_STATES
        and state != "알 수 없음"
        and state_conf >= CONTRADICTION_THRESHOLD
    ):
        flags.append({
            "type": "contradiction",
            "detail": (
                f"질환 모델: 정상 판정 / "
                f"상태 모델: '{state}' {state_conf:.0%} 탐지 — 두 모델 결과 불일치"
            ),
        })

    # --- 결과 종합 ---
    is_uncertain = len(flags) > 0

    if any(f["type"] == "contradiction" for f in flags):
        reason = "질환·상태 모델 간 결과 불일치"
    elif flags:
        reason = f"모델 신뢰도 임계값({CONF_THRESHOLD}) 미만"
    else:
        reason = "정상 범위 내 결과"

    return {
        "is_uncertain": is_uncertain,
        "reason": reason,
        "flags": flags,
        "top_classes": {
            "피부 타입": f"{skin_type} ({type_conf:.0%})",
            "피부 질환": f"{disease} ({disease_conf:.0%})",
            "피부 상태": f"{state} ({state_conf:.0%})",
        },
    }
