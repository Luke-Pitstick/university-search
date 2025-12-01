from cache.semantic_caching import SemanticCache
from utils.general_utils import SearchResult
from llm.llm import NormalSearch

    


class UniversityEngine:
    def __init__(self):
        self.semantic_cache = SemanticCache()
        self.normal_search = NormalSearch()
        
    def hybrid_search(self, query) -> SearchResult:
        result = self.normal_search.search(query)
        return result
    
    def semantic_search(self, query) -> SearchResult:
        result = self.semantic_cache.search(query)
        return result
        
    def search(self, query):
        # Check Semantic Cache for cached result
        result = self.semantic_search(query)
        
        if result.similarity >= 0.8:
            return result
        
        # If not then normal search
        result = self.hybrid_search(query)
        self.semantic_cache.cache(query, result)
        
        return result