# Credits from https://medium.com/@nepalsakshi05/taking-chroma-reranking-to-the-next-level-with-a-hybrid-retrieval-system-b24ca9eb1a28
import re
from langchain_chroma import Chroma
from langchain_core.documents import Document
from typing import List
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_community.retrievers import BM25Retriever
from sentence_transformers import CrossEncoder


class HybridSearchEngine:
    def __init__(self, chroma_db_path: str, vector_store_path: str, collection_name: str, top_k: int = 10):
        self.chroma_db_path = chroma_db_path
        self.vector_store_path = vector_store_path
        self.top_k = top_k
        self.collection_name = collection_name
        self.embeddings = OllamaEmbeddings(model = 'mxbai-embed-large')
        self.client = Chroma(persist_directory=chroma_db_path, embedding_function=self.embeddings)
        self.all_docs = self._load_all_docs(collection_name)
        # Replaced ragatouille with sentence-transformers for better compatibility
        self._cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        
        # Default weights for fusion
        self._default_weights = {
            "vector": 0.4,
            "bm25": 0.1,
            "rerank": 0.4,
            "context": 0.1
        }
        
    def _load_all_docs(self, collection_name: str) -> List[Document]:
        # Access the underlying client directly to get all documents
        # Note: Chroma wrapper might not expose get() directly on the client object the same way
        # But assuming the previous code intended to use the collection:
        # We need to access the collection object. langchain_chroma.Chroma doesn't have get_or_create_collection directly usually, 
        # it wraps it. We might need to access ._client if it exists or use the valid API.
        # However, for now preserving intent of original code but fixing variable name.
        # If self.client is a langchain Chroma object:
        return self.client._client.get_or_create_collection(collection_name).get()

    def _preprocess_query(self, query: str) -> str:
        query = query.strip().lower()
        query = re.sub(r'[^\w\s?!]', '', query)  # Strip special characters
        return " ".join(query.split())  # Remove extra spaces
    
    async def _retrieve_vector(self, query: str) -> List[Document]:
        query_embedding = self.embeddings.embed_query(query)
        # Using the langchain wrapper's interface if possible, or underlying client
        # Original code tried to use self._client which wasn't defined.
        # Assuming self.client is langchain Chroma.
        # But query method is on the collection.
        results = self.client._client.get_or_create_collection(self.collection_name).query(
            query_embeddings=[query_embedding],
            n_results=self.top_k * 2,
            include=["documents", "metadatas", "distances"]
        )
        # results["documents"][0] is a list of strings
        return [Document(page_content=doc, metadata=meta | {"vector_score": max(0, 1 - dist)})
                for doc, dist, meta in zip(results["documents"][0], results["distances"][0], results["metadatas"][0])]
    
    
    async def _retrieve_bm25(self, query: str) -> List[Document]:
        # BM25Retriever expects a list of Documents
        # We need to convert the raw data from _load_all_docs to Documents
        raw_docs = self.all_docs
        # raw_docs from chroma .get() is a dict with 'documents', 'metadatas', etc.
        docs_objects = []
        if raw_docs and 'documents' in raw_docs and raw_docs['documents']:
             for i, content in enumerate(raw_docs['documents']):
                 meta = raw_docs['metadatas'][i] if raw_docs['metadatas'] else {}
                 docs_objects.append(Document(page_content=content, metadata=meta))
                 
        bm25_retriever = BM25Retriever.from_documents(docs_objects)
        bm25_retriever.k = self.top_k * 2
        return bm25_retriever.invoke(query)
    
    def _rerank(self, query: str, docs: List[Document]) -> List[Document]:
        if not docs:
            return []
        pairs = [[query, doc.page_content] for doc in docs]
        scores = self._cross_encoder.predict(pairs)
        for doc, score in zip(docs, scores):
            doc.metadata["rerank_score"] = float(score)
        return docs
    
    def _contextual_similarity(self, query: str, docs: List[Document]) -> List[Document]:
        query_terms = set(self._preprocess_query(query).split())
        for doc in docs:
            doc_terms = set(doc.page_content.lower().split())
            overlap = len(query_terms & doc_terms) / max(len(query_terms), 1)
            doc.metadata["context_score"] = overlap
        return docs
    
    def _normalize_scores(self, docs: List[Document]) -> List[Document]:
        for method in ["vector", "bm25", "rerank", "context"]:
            scores = [doc.metadata.get(f"{method}_score", 0) for doc in docs]
            if not scores:
                continue
            if max(scores) > min(scores):
                normalized = [(s - min(scores)) / (max(scores) - min(scores) + 1e-6) for s in scores]
                for doc, norm_score in zip(docs, normalized):
                    doc.metadata[f"{method}_score"] = norm_score
        return docs
    
    def _advanced_fusion(self, docs: List[Document]) -> List[Document]:
        for doc in docs:
            doc.metadata["final_score"] = sum(
                self._default_weights[m] * doc.metadata.get(f"{m}_score", 0)
                for m in self._default_weights
            )
        return sorted(docs, key=lambda x: x.metadata["final_score"], reverse=True)[:self.top_k]
    
    async def search(self, query: str) -> List[Document]:
        query = self._preprocess_query(query)
        vector_docs = await self._retrieve_vector(query)
        # bm25_docs = await self._retrieve_bm25(query) # Not using bm25 results for fusion input directly in this flow?
        # The original code passed vector_docs to rerank.
        # It seems it only reranked vector results.
        # And it computed BM25 but didn't seem to merge the lists of documents?
        # Wait, the original code:
        # vector_docs = await self._retrieve_vector(query)
        # bm25_docs = await self._retrieve_bm25(query)
        # colbert_docs = await self._colbert_rerank(query, vector_docs) 
        # Only vector_docs were reranked. bm25_docs were calculated but unused in the chain unless implicit.
        
        # To make BM25 useful, we should probably merge them or at least score them. 
        # But sticking to the original logic flow for now, just fixing the bugs.
        # Actually, if we want hybrid search, we should probably combine vector_docs and bm25_docs before reranking.
        
        # Let's combine unique documents from both sources
        bm25_docs = await self._retrieve_bm25(query)
        
        # Simple deduplication by content or ID if available. 
        # Using content for now as IDs might not be consistent.
        seen_contents = set()
        combined_docs = []
        for doc in vector_docs + bm25_docs:
            if doc.page_content not in seen_contents:
                seen_contents.add(doc.page_content)
                combined_docs.append(doc)

        reranked_docs = self._rerank(query, combined_docs)
        contextual_docs = self._contextual_similarity(query, reranked_docs)
        normalized_docs = self._normalize_scores(contextual_docs)
        return self._advanced_fusion(normalized_docs)
