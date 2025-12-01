from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from utils.general_utils import SearchResult
from loguru import logger
import uuid



class SemanticCache:
    def __init__(self, chroma_db_path: str = './chroma_cache', threshold: float = 0.45):
        self.chroma_db_path: str = chroma_db_path
        self.embeddings: OllamaEmbeddings = self._initialize_embeddings()
        self.vector_store: Chroma = self._initialize_chroma(self.chroma_db_path)
        
        self.threshold = threshold
    
    def _initialize_embeddings(self) -> OllamaEmbeddings:
        logger.info("Initializing embedding model.")
        embeddings = OllamaEmbeddings(model = 'mxbai-embed-large')
        logger.info("Model Initialized!")
        return embeddings
    
    def _initialize_chroma(self, path) -> Chroma:
        logger.info("Initializing Chroma DB.")
        chroma = Chroma("cache_db", persist_directory = path, embedding_function = self.embeddings)
        logger.info("Chroma Initialized!")
        return chroma
    
    def search(self, query):
        results = self.vector_store.similarity_search_with_score(query, k = 1)
        
        if not results:
            return None
        
        # Check threshold
        
        best_doc, score = results[0]
        
        if score < self.threshold:
            logger.info("Cache Hit!")
            result = SearchResult(score, best_doc)
            return result
        
        logger.info("Cache Miss (Score too high/distance too far).")
        return None
        
    def cache(self, query: str, result: str) -> bool:
        doc = Document(
            page_content = query,
            metadata = {
                "model_result": result
            },
            id = str(uuid.uuid4())
        )
        
        ids = self.vector_store.add_documents([doc])
        
        if len(ids) > 0:
            logger.info(f"Cached query with ID: {ids[0]}")
            return True
        
        return False