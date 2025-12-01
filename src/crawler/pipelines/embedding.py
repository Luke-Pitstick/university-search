from scrapy.crawler import Crawler
from scrapy.settings import Settings

from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_core.documents import Document


class EmbeddingPipeline:
    def __init__(self, settings: Settings):
        print("Starting EmbeddingPipeline")
        self.embeddings = OllamaEmbeddings(model = 'mxbai-embed-large')
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size = 750, chunk_overlap = 150)   
        print("EmbeddingPipeline initialized")
        
    @classmethod
    def from_crawler(cls, crawler: Crawler):
        # Retrieve the settings object from the crawler
        settings = crawler.settings
        
        # Instantiate the pipeline by passing the settings object
        return cls(settings)
    
    
    def make_document(self, item):
        content = f"Title: {item['title']}\n\nURL: {item['url']}\n\nContent: {item['text']}"
        metadata = {"url": item["url"], "title": item["title"], "source": "scrapy crawl cuboulder"}
        document = Document(page_content=content, metadata=metadata)
        return document
    
    def embed_document(self, document):
        text_chunks = self.text_splitter.split_documents([document])
        texts = [chunk.page_content for chunk in text_chunks]
        
        embeddings = self.embeddings.embed_documents(texts)
        return list(zip(text_chunks, embeddings))
        
    def process_page(self, item):
        document = self.make_document(item)
        chunk_embeddings = self.embed_document(document)

        results = []
        for chunk, emb in chunk_embeddings:
            results.append({
                "text": chunk.page_content,
                "embedding": emb
            })
        
        return results

    def process_item(self, item, spider):
        spider.logger.info(f"EmbeddingPipeline: Processing item {item['url']}")
        item['embeddings'] = self.process_page(item)
        return item