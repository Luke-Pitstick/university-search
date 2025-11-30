from langchain_chroma import Chroma
from scrapy.crawler import Crawler
from scrapy.settings import Settings
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_core.documents import Document
import uuid

class VectorStorePipeline:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.db_location = "./chroma_langchain_db"
        self.university_name = settings.get('UNIVERSITY_NAME')
        print("Starting VectorStorePipeline")
        self.vector_store = Chroma(collection_name = self.university_name, persist_directory = self.db_location, embedding_function=None)  
        print("VectorStorePipeline initialized")
    @classmethod
    def from_crawler(cls, crawler: Crawler):
        # Retrieve the settings object from the crawler
        settings = crawler.settings
        
        # Instantiate the pipeline by passing the settings object
        return cls(settings)
    
    
    
    def process_item(self, item, spider):
        spider.logger.info(f"VectorStorePipeline: Storing data for {item['url']}")
        
        texts = [chunk["text"] for chunk in item["embeddings"]]
        embeddings = [chunk["embedding"] for chunk in item["embeddings"]]
        metadatas = [
            {"url": item["url"], 
             "title": item.get("title", ""), 
             "source": "university_scraper"} 
            for _ in item["embeddings"]
        ]
        ids = [str(uuid.uuid4()) for _ in item["embeddings"]]
        
        self.vector_store.add_texts(texts=texts, metadatas=metadatas, ids=ids, embeddings=embeddings)
        return item
    