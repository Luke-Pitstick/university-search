from langchain_core.documents import Document

class SearchResult:
    def __init__(self, similarity, document: Document) -> None:
        self.similarity: float = similarity
        self.doc: Document = document
        