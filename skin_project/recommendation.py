from fastapi import Body, APIRouter, Depends
from sqlalchemy.orm import Session
from schemas import RecommendAIRequest
from sentence_transformers import SentenceTransformer
from groq import AsyncGroq
from pinecone import Pinecone
import os
import asyncio
from dotenv import load_dotenv

router = APIRouter()

# 환경변수 로딩
load_dotenv('config.env')

# API 키 없으면 추천 기능 비활성화 (시작 시 모델 로드 안 함)
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

model = None
client = None
pc = None

if PINECONE_API_KEY and GROQ_API_KEY:
    model = SentenceTransformer("jhgan/ko-sbert-nli")
    client = AsyncGroq(api_key=GROQ_API_KEY)
    pc = Pinecone(api_key=PINECONE_API_KEY)
else:
    print("⚠️ GROQ_API_KEY 또는 PINECONE_API_KEY 미설정. 추천 기능 비활성화.")

INDEXES = {
    "토너": "toner",
    "앰플": "ampoule",
    "크림": "cream"
}

# 데이터베이스 세션 의존성
def get_db():
    from database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/recommend/ai")
async def recommend_ai(data: RecommendAIRequest = Body(...), db: Session = Depends(get_db)):
    # Pinecone API 키 확인
    if not pc or not client:
        return {
            "error": "GROQ_API_KEY 또는 PINECONE_API_KEY가 설정되지 않았습니다. 관리자에게 문의하세요.",
            "분석 요약": "API 키 설정이 필요합니다.",
            "추천 리스트": []
        }

    # 1. Pinecone 검색 (GPT 호출과 병렬 실행 위해 먼저 준비)
    query_text = f"{data.skin_type} 피부 / 민감도: {data.sensitivity} / 상태: {', '.join(data.diagnosis)}"
    query_embedding = model.encode(query_text).tolist()

    gpt_product_prompt = ""
    product_map = {}

    for category, index_name in INDEXES.items():
        index = pc.Index(index_name)
        result = index.query(vector=query_embedding, top_k=10, include_metadata=True)
        matches = result.get("matches", [])
        if not matches:
            continue
        best = max(matches, key=lambda x: x["score"])
        meta = best["metadata"]
        product_name = meta.get("product_name", "")
        product_review = meta.get("review", "")

        product_info = {
            "카테고리": category,
            "제품명": product_name,
            "이미지": meta.get("image_url", ""),
            "링크": meta.get("link", ""),
            "피부타입": meta.get("skin_type", "")
        }
        product_map[category] = product_info
        gpt_product_prompt += f"{category}: {product_name} - {product_review}\n"

    # 2. GPT 2번 호출을 병렬 처리 (약 40% 속도 단축)
    analysis_prompt = (
        f"피부 타입: {data.skin_type}, 민감도: {data.sensitivity}, 피부 고민: {', '.join(data.diagnosis)}\n"
        "위 정보를 바탕으로 사용자의 피부 상태를 간단하게 분석한 결과를 3~4줄 이내 요약해줘. 이모지, 말투 없이 전문가처럼."
    )
    gpt_prompt = (
        f"피부 타입: {data.skin_type}, 민감도: {data.sensitivity}, 피부 고민: {', '.join(data.diagnosis)}\n"
        f"추천 제품 및 리뷰:\n{gpt_product_prompt}\n"
        "각 제품의 리뷰를 바탕으로 추천 이유를 각 제품별로 한 문장씩 정리해줘.\n"
        "그리고 연고 1개, 피부과 시술 2개도 이름과 추천 이유를 포함해 각각 한 문장씩 추천해줘."
    )

    analysis_response, gpt_response = await asyncio.gather(
        client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": analysis_prompt}],
            temperature=0.3,
            max_tokens=300
        ),
        client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": gpt_prompt}],
            temperature=0.3,
            max_tokens=600
        )
    )

    gpt_text = gpt_response.choices[0].message.content.strip()
    gpt_lines = [line.strip("- ") for line in gpt_text.split("\n") if line.strip()]

    enriched_list = []
    used_categories = set()

    for line in gpt_lines:
        for category, info in product_map.items():
            if category in used_categories:
                continue
            if category in line or info["제품명"].split()[0] in line:
                info["추천이유"] = line.split("-", 1)[-1].strip()
                enriched_list.append(info)
                used_categories.add(category)
                break

    for line in gpt_lines:
        if line.startswith("연고"):
            enriched_list.append({
                "카테고리": "연고",
                "제품명": line.split(":")[0].split("|")[-1].strip(),
                "추천이유": line.split(":")[-1].strip(),
                "이미지": "",
                "링크": ""
            })
        elif any(kw in line for kw in ["시술", "토닝", "필링"]):
            enriched_list.append({
                "카테고리": "시술",
                "제품명": line.split(":")[0].strip(),
                "추천이유": line.split(":")[-1].strip()
            })

    # 4. 추천 결과를 DB에 자동 저장
    try:
        from crud import create_recommendation_history
        
        # 추천 내역 저장용 데이터 구성
        recommendation_data = {
            "user_id": getattr(data, 'user_id', 1),  # 임시 사용자 ID
            "skin_type": data.skin_type,
            "sensitivity": data.sensitivity,
            "concerns": data.diagnosis,
            "ai_explanation": analysis_response.choices[0].message.content.strip(),
            "recommended_products": [
                {
                    "product_name": item.get("제품명", ""),
                    "product_brand": "AI 추천",  # 브랜드 정보가 없으므로 기본값
                    "product_category": item.get("카테고리", ""),
                    "reason": item.get("추천이유", "")
                } for item in enriched_list
            ]
        }
        
        saved_history = create_recommendation_history(db, recommendation_data)
        print(f"✅ AI 추천 결과 자동 저장 완료: ID {saved_history.id}")
        
    except Exception as save_error:
        print(f"⚠️ 추천 내역 저장 실패: {save_error}")
        # 저장 실패해도 추천 결과는 반환

    return {
        "분석 요약": analysis_response.choices[0].message.content.strip(),
        "추천 리스트": enriched_list
    }
