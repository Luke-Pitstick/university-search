import chromadb

def verify_chromadb_exists(chroma_db_path: str) -> bool:
    client = chromadb.PersistentClient(chroma_db_path)
    return client.list_collections()

def verify_collection_exists(chroma_db_path: str, collection_name: str) -> bool:
    client = chromadb.PersistentClient(chroma_db_path)
    return client.get_collection(collection_name)

if __name__ == "__main__":
    print(verify_collection_exists("../../../chroma_langchain_db", "mit"))