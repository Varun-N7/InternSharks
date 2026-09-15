import faiss
import numpy as np


class VectorStore:
    def __init__(self):
        self.documents = {}

    def add_document(
        self,
        document_id: str,
        file_name: str,
        chunks: list[str],
        embeddings,
    ):
        if not chunks:
            raise ValueError("No chunks to store")

        vectors = np.array(embeddings, dtype="float32")

        dimension = vectors.shape[1]

        index = faiss.IndexFlatIP(dimension)
        index.add(vectors)

        self.documents[document_id] = {
            "file_name": file_name,
            "chunks": chunks,
            "index": index,
        }

    def document_exists(self, document_id: str) -> bool:
        return document_id in self.documents

    def get_document(self, document_id: str):
        return self.documents.get(document_id)

    def search(
        self,
        document_id: str,
        query_embedding,
        top_k: int = 3,
    ) -> list[str]:

        document = self.documents.get(document_id)

        if not document:
            raise ValueError("Document not found")

        query_vector = np.array(
            [query_embedding],
            dtype="float32",
        )

        total_chunks = len(document["chunks"])
        top_k = min(top_k, total_chunks)

        scores, indexes = document["index"].search(
            query_vector,
            top_k,
        )

        results = []

        for index in indexes[0]:
            if index != -1:
                results.append(document["chunks"][index])

        return results

    def delete_document(self, document_id: str):
        if document_id in self.documents:
            del self.documents[document_id]


vector_store = VectorStore()