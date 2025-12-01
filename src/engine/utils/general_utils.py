from langchain_core.documents import Document

class SemanticSearchResult:
    def __init__(self, similarity, document: Document) -> None:
        self.similarity: float = similarity
        self.doc: Document = document
        
class NormalSearchResult:
    def __init__(self, response: str, docs: list[Document]) -> None:
        self.response: str = response
        self.docs: list[Document] = docs