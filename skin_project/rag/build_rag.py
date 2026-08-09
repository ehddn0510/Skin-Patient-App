"""
skin_knowledge.txt를 읽어 토픽/섹션 단위로 분할한 후
ChromaDB에 임베딩하여 저장합니다.
Docker 빌드 시 또는 최초 1회만 실행합니다.
"""
import re
import os
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

BASE_DIR = os.path.dirname(__file__)
DOCS_PATH = os.path.join(BASE_DIR, "docs", "skin_knowledge.txt")
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")
COLLECTION_NAME = "skin_knowledge"
EMBEDDING_MODEL = "jhgan/ko-sroberta-multitask"

# 각 주제의 실제 출처 (근거 인용 및 검증용)
SOURCE_URLS = {
    "여드름": "https://health.kdca.go.kr/healthinfo/biz/health/gnrlzHealthInfo/gnrlzHealthInfo/gnrlzHealthInfoView.do?cntnts_sn=3947",
    "입술건조(구순염)": "https://www.amc.seoul.kr/asan/healthinfo/disease/diseaseDetail.do?contentId=32151",
}


def parse_chunks(text: str) -> list[dict]:
    """
    [토픽] 블록 → 섹션명) 단위로 분할하여 청크 리스트 반환.
    각 청크: {id, text, topic, section}
    """
    chunks = []
    topic_blocks = re.split(r'\[([^\]]+)\]', text)
    # split 결과: ['', '여드름', '\n개요)...', '지루성 피부염', '\n개요)...', ...]

    i = 1
    while i < len(topic_blocks) - 1:
        topic = topic_blocks[i].strip()
        content = topic_blocks[i + 1]

        # 섹션명) 패턴으로 분할
        parts = re.split(r'\n([가-힣a-zA-Z ]+\))\n', content)
        # parts[0]: 섹션 이전 텍스트(보통 빈 줄), parts[1]: 섹션명, parts[2]: 내용, ...

        j = 1
        while j < len(parts) - 1:
            section = parts[j].replace(')', '').strip()
            body = parts[j + 1].strip()

            if len(body) > 30:
                chunk_text = f"[{topic}] {section}: {body[:600]}"
                chunks.append({
                    "id": f"{topic}_{section}",
                    "text": chunk_text,
                    "topic": topic,
                    "section": section,
                    "source_url": SOURCE_URLS.get(topic, ""),
                })
            j += 2

        i += 2

    return chunks


def build():
    print("📚 RAG 빌드 시작...")

    with open(DOCS_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = parse_chunks(text)
    print(f"📄 청크 {len(chunks)}개 생성")
    for c in chunks:
        print(f"   - {c['id']}")

    embedding_fn = SentenceTransformerEmbeddingFunction(EMBEDDING_MODEL)
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    try:
        client.delete_collection(COLLECTION_NAME)
        print("🗑️  기존 컬렉션 삭제")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"},
    )

    collection.add(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[
            {"topic": c["topic"], "section": c["section"], "source_url": c["source_url"]}
            for c in chunks
        ],
    )

    print(f"✅ ChromaDB 저장 완료 → {CHROMA_PATH}")
    print(f"   컬렉션: {COLLECTION_NAME} | 문서 수: {len(chunks)}")


if __name__ == "__main__":
    build()
