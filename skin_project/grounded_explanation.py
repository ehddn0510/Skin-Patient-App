"""
질환/상태 진단 결과를 RAG 근거 위에서만 설명합니다.
RAG 매칭이 없거나 모델 간 불확실성이 감지되면 LLM 생성 없이 전문의 상담으로 안내합니다.
"""
import os
from groq import AsyncGroq
from dotenv import load_dotenv
from rag.rag_pipeline import rag_pipeline

load_dotenv('config.env')

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

client = AsyncGroq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

NORMAL_DISEASE = {"정상", "알 수 없음"}
NORMAL_STATE = {"양호", "알 수 없음"}

# 설명 게이트에 반영할 불확실성 신호. 피부 타입 모델은 신뢰도가 구조적으로 낮아
# 항상 low_confidence가 뜨므로 제외하고, 질환/상태 자체의 문제만 본다.
RELEVANT_MODELS = {"피부 질환", "피부 상태"}

# 근거 기반 설명을 제공하는 대상은 임상적으로 진단 기준이 명확한 항목으로 한정한다.
# 주름·처짐(chin_sagging)처럼 정도(degree)와 심미적 판단이 개입되는 항목은
# 신뢰도가 높게 나오더라도 의도적으로 제외한다 — RAG 코퍼스가 이를 다루지 않기도 하고,
# 애초에 "확신에 찬 근거"를 만들기 부적절한 영역이라 판단했기 때문이다.
GROUNDING_ELIGIBLE_TOPICS = {"여드름", "염증성", "병변", "입술건조"}


def _is_diagnosis_uncertain(uncertainty: dict) -> bool:
    """질환/상태 설명과 직접 관련된 불확실성 신호만 판단합니다."""
    return any(
        f["type"] == "contradiction" or f.get("model") in RELEVANT_MODELS
        for f in uncertainty.get("flags", [])
    )


async def generate_grounded_explanation(disease: str, state: str, uncertainty: dict) -> dict:
    """
    감지된 질환/상태에 대해 RAG 지식으로 근거가 확인될 때만 LLM 설명을 생성합니다.

    Returns:
        available=True:  {"available": True, "topic", "similarity", "explanation"}
        available=False: {"available": False, "message"}
    """
    query = disease if disease not in NORMAL_DISEASE else (state if state not in NORMAL_STATE else None)

    if query is None:
        return {"available": False, "message": "특이 소견이 없습니다."}

    if query not in GROUNDING_ELIGIBLE_TOPICS:
        return {
            "available": False,
            "message": "이 항목은 정도·심미적 판단이 개입되어 근거 기반 설명 대상에서 제외됩니다. 전문의 상담을 권장합니다.",
        }

    if _is_diagnosis_uncertain(uncertainty):
        return {
            "available": False,
            "message": "질환/상태 판정 결과가 불확실하여 근거 기반 설명을 생략합니다. 전문의 상담을 권장합니다.",
        }

    rag_result = rag_pipeline.search(query)
    if not rag_result.get("found"):
        return {
            "available": False,
            "message": rag_result.get("message", "관련 정보가 없습니다. 전문의 상담을 권장합니다."),
        }

    if client is None:
        # RAG 근거는 찾았지만 GROQ_API_KEY 미설정 → 원문 그대로 반환
        return {
            "available": True,
            "topic": rag_result["topic"],
            "similarity": rag_result["similarity"],
            "explanation": rag_result["content"],
            "source_url": rag_result.get("source_url", ""),
        }

    prompt = (
        f"아래는 '{rag_result['topic']}'에 대한 신뢰할 수 있는 참고 자료입니다.\n\n"
        f"{rag_result['content']}\n\n"
        "위 자료에 있는 내용만 근거로 사용해서, 사용자에게 진단 결과를 3문장 이내로 "
        "친절하게 설명해줘. 자료에 없는 내용은 추측하지 말고, 반드시 전문의 상담을 권장하는 "
        "문장으로 마무리해줘."
    )

    try:
        response = await client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=300,
        )
        explanation = response.choices[0].message.content.strip()
    except Exception:
        explanation = rag_result["content"]

    return {
        "available": True,
        "topic": rag_result["topic"],
        "similarity": rag_result["similarity"],
        "explanation": explanation,
        "source_url": rag_result.get("source_url", ""),
    }
