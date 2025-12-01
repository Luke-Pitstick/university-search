from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from operator import itemgetter
from langchain_community.retrievers import BM25Retriever  # pyright: ignore[reportMissingImports]
from loguru import logger  # pyright: ignore[reportMissingImports]

def format_docs(docs):
    return "\n\n---\n\n".join(doc.page_content for doc in docs)

class NormalSearch:
    def __init__(self, chroma_db_path: str = '../../../chroma_langchain_db', university_name: str = "stanford", k: int = 10):
        # General Variables
        logger.info(f"Initializing NormalSearch")
        self.university_name = ""
        self.chroma_db_path = chroma_db_path
        self.embeddings = OllamaEmbeddings(model="mxbai-embed-large")
        self.vector_store = self._initialize_chroma(self.chroma_db_path)
        self.top_k = k
        self.chroma_retriever = self.vector_store.as_retriever(
            search_type = "similarity", 
            search_kwargs = {"k": self.top_k}
        )
        self.bm25retriever = BM25Retriever
        self.llm = OllamaLLM(model="gemma3:4b")
        logger.info(f"NormalSearch Initialized")
    
        
        # LLM Chain
        system_template = """
        You are a helpful assistant answering questions about school based on the provided context.
        Please provide a comprehensive, well-structured answer to the user's question.

        INSTRUCTIONS:
        1. Answer the question based primarily on the provided context
        2. If the context doesn't contain enough information, say so clearly
        3. Organize your answer with clear headings and bullet points when appropriate
        4. Be concise but thorough
        5. Include specific details from the sources
        """

        human_template = """
        CONTEXT:
        {context}

        USER QUESTION: {question}

        ANSWER:
        """

        system_message = SystemMessagePromptTemplate.from_template(system_template)
        human_message = HumanMessagePromptTemplate.from_template(human_template)


        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                system_message,
                human_message
            ]
        )
        
        self.rag_chain = (
            RunnablePassthrough.assign(
                context=itemgetter("question") | self.chroma_retriever | format_docs
            )
            | self.prompt_template
            | self.llm
            | StrOutputParser()
        )

        
    def _initialize_chroma(self, path) -> Chroma:
        logger.info("Initializing Chroma DB.")
        chroma = Chroma("cache_db", persist_directory = path, embedding_function = self.embeddings)
        logger.info("Chroma Initialized!")
        return chroma
    
    
    def query(self, user_query):
        logger.info(f"Querying NormalSearch with query: {user_query}")
        response = self.rag_chain.invoke({"question": user_query})
        logger.info(f"NormalSearch response: {response}")
        return response