from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from operator import itemgetter
from langchain_community.retrievers import BM25Retriever  # pyright: ignore[reportMissingImports]
from loguru import logger  # pyright: ignore[reportMissingImports]
import os
import sys
from dataclasses import dataclass

from utils.general_utils import NormalSearchResult
from tests.verify_chromadb_exists import verify_chromadb_exists
@dataclass
class SearchConfig:
    db_path: str = "../../chroma_langchain_db"
    university_name: str = "stanford"
    embedding_model: str = "mxbai-embed-large"
    llm_model: str = "llama3.2"
    top_k: int = 5

def format_docs(docs):
    return "\n\n---\n\n".join(doc.page_content for doc in docs)

class NormalSearch:
    def __init__(self, config: SearchConfig):
        self.config = config
        self._validate_paths()
        
        logger.info(f"Initializing NormalSearch with config: {self.config}")
        
        self.embeddings = OllamaEmbeddings(model=self.config.embedding_model)
        self.vector_store = self._initialize_chroma(self.config.db_path, self.config.university_name)
        self.llm = OllamaLLM(model=self.config.llm_model)
        
        
        # Uncomment to test the vector store
        #print(self.vector_store.get())
        
        # Build the chain immediately
        self.rag_chain = self._build_chain()
        logger.info(f"NormalSearch Initialized")
    
        
    
    def _get_prompt_template(self) -> ChatPromptTemplate:
        """Defines the prompt structure."""
        system_template = """
        You are a helpful academic assistant. Use the following context to answer the user's question.
        
        Guidelines:
        - If the answer is not in the context, state that you do not know.
        - Use bullet points for clarity.
        - Be concise.
        """
        
        # Using the standard ChatPromptTemplate.from_messages syntax
        return ChatPromptTemplate.from_messages([
            ("system", system_template),
            ("human", "Context:\n{context}\n\nQuestion: {question}")
        ])

    def _build_chain(self):
        retriever = self._get_retriever()
        prompt = self._get_prompt_template()

        retrieval_step = RunnableParallel(
            {"docs": itemgetter("question") | retriever, "question": itemgetter("question")}
        )

        answer_step = RunnablePassthrough.assign(
            answer=(
                RunnablePassthrough.assign(
                    context=itemgetter("docs") | RunnableLambda(format_docs)
                )
                | prompt
                | self.llm
                | StrOutputParser()
            )
        )

        chain = retrieval_step | answer_step
        
        return chain
    
    def _get_retriever(self):
        return self.vector_store.as_retriever(
            search_type = "similarity", 
            search_kwargs = {"k": self.config.top_k}
        )
    
    def _validate_paths(self):
        if not os.path.exists(self.config.db_path):
            logger.warning(f"Chroma DB path does not exist: {self.config.db_path}")
        
    def _initialize_chroma(self, path, university_name) -> Chroma:
        logger.info("Initializing Chroma DB.")
        chroma = Chroma(collection_name=university_name, persist_directory = path, embedding_function = self.embeddings)
        logger.info("Chroma Initialized!")
        return chroma
    
    
    def query(self, user_query) -> NormalSearchResult:
        logger.info(f"Querying: {user_query}")
        try:
            response = self.rag_chain.invoke({"question": user_query})
            output = NormalSearchResult(response['answer'], response['docs'])
            return output
        except Exception as e:
            logger.error(f"Error during query execution: {e}")
            return NormalSearchResult(None, "An error occurred while processing your request.")
        


if __name__ == "__main__":
    config = SearchConfig(
        db_path = "../../chroma_langchain_db",
        university_name = "stanford",
        embedding_model = "mxbai-embed-large",
        llm_model = "gemma3:4b",
        top_k = 5
    )
    normal_search = NormalSearch(config)
    print(verify_chromadb_exists(config.db_path))