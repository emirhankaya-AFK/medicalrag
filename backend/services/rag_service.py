import chromadb
from typing import List, Dict, Any, Optional
from ..config.settings import settings
from .llm_service import llm_service

class MedicalRAGService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_DIR)
        self.collection_name = "medical_records"
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_record_chunks(self, record_id: int, patient_id: int, text: str):
        """
        Splits the text into chunks of ~1000 characters with 200 character overlap
        and indexes them with patient metadata filters.
        """
        if not text.strip():
            return

        # Simple chunking
        chunk_size = 1000
        overlap = 200
        chunks = []
        
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap

        ids = []
        embeddings = []
        metadatas = []
        documents = []

        for idx, chunk in enumerate(chunks):
            chunk_id = f"rec_{record_id}_chunk_{idx}"
            embedding = llm_service.generate_embeddings(chunk)

            ids.append(chunk_id)
            embeddings.append(embedding)
            metadatas.append({
                "record_id": record_id,
                "patient_id": patient_id
            })
            documents.append(chunk)

        if ids:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )

    def query_record_chunks(self, query_text: str, patient_id: int, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Queries ChromaDB for clinical relevance, strictly filtered by patient_id.
        """
        query_embedding = llm_service.generate_embeddings(query_text)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where={"patient_id": patient_id}
        )

        formatted_results = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)
            ids = results["ids"][0]

            for i in range(len(docs)):
                formatted_results.append({
                    "id": ids[i],
                    "content": docs[i],
                    "metadata": metas[i],
                    "distance": distances[i]
                })

        return formatted_results

    def delete_record_chunks(self, record_id: int):
        self.collection.delete(
            where={"record_id": record_id}
        )

rag_service = MedicalRAGService()
