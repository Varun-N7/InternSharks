from sentence_transformers import SentenceTransformer

from app.config import EMBEDDING_MODEL


class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)

    def create_embeddings(self, texts: list[str]):
        if not texts:
            raise ValueError("No text provided for embedding")

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
        )

        return embeddings


embedding_service = EmbeddingService()