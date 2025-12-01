from llm.normal_search import NormalSearch, SearchConfig
from tests.verify_chromadb_exists import verify_collection_exists

config = SearchConfig(
        db_path = "../../chroma_langchain_db",
        university_name = "unt",
        embedding_model = "mxbai-embed-large",
        llm_model = "gemma3:4b",
        top_k = 5
    )

def test_normal_search(config: SearchConfig):
    normal_search = NormalSearch(config)
    
    while True:
        query = input("Enter a question (or 'exit' to quit): ")
        if query == "exit":
            break
        result = normal_search.query(query)
        print(result.response)
        for doc in result.docs:
            print(doc.metadata['url'])
    
if __name__ == "__main__":
    print(verify_collection_exists(config.db_path, config.university_name))
    test_normal_search(config)
    print("Exiting...")