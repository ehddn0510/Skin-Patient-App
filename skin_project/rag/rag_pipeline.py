"""
ChromaDB에서 쿼리와 관련된 피부 지식을 검색합니다.

유사도 판단:
  ChromaDB cosine distance → similarity = 1 - distance (0~1)
  SIMILARITY_THRESHOLD 미만이면 관련 문서 없음으로 처리
  → 근거 없는 의료 정보 생성 방지, 전문의 상담으로 안내
"""
import os
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

BASE_DIR = os.path.dirname(__file__)
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")
COLLECTION_NAME = "skin_knowledge"
EMBEDDING_MODEL = "jhgan/ko-sroberta-multitask"
SIMILARITY_THRESHOLD = 0.5  # 이 값 미만이면 관련 문서 없음으로 판단


class RAGPipeline:
    def __init__(self):
        self._collection = None

    def _get_collection(self):
        if self._collection is None:
            embedding_fn = SentenceTransformerEmbeddingFunction(EMBEDDING_MODEL)
            client = chromadb.PersistentClient(path=CHROMA_PATH)
            self._collection = client.get_collection(
                name=COLLECTION_NAME,
                embedding_function=embedding_fn,
            )
        return self._collection

    def search(self, query: str, n_results: int = 2) -> dict:
        """
        쿼리와 관련된 문서를 검색합니다.

        Returns:
            found=True:  {"found": True, "topic", "content", "similarity"}
            found=False: {"found": False, "message"}
        """
        try:
            collection = self._get_collection()
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "distances", "metadatas"],
            )

            docs = results["documents"][0]
            if not docs:
                return {
                    "found": False,
                    "message": "관련 정보가 없습니다. 피부과 전문의 상담을 권장합니다.",
                }

            # cosine distance(0~1) → similarity(0~1)
            distance = results["distances"][0][0]
            similarity = round(1 - distance, 3)

            if similarity < SIMILARITY_THRESHOLD:
                return {
                    "found": False,
                    "similarity": similarity,
                    "message": "정확히 일치하는 정보가 없습니다. 피부과 전문의 상담을 권장합니다.",
                }

            meta = results["metadatas"][0][0]
            return {
                "found": True,
                "topic": meta.get("topic", ""),
                "section": meta.get("section", ""),
                "content": docs[0],
                "similarity": similarity,
                "source_url": meta.get("source_url", ""),
            }

        except Exception as e:
            return {"found": False, "message": f"검색 오류: {str(e)}"}


rag_pipeline = RAGPipeline()
