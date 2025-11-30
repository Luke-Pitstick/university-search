import os
import shutil
import chromadb

def clear_chroma_db(db_location):
    if os.path.exists(db_location):
        shutil.rmtree(db_location)
    

def clear_chroma_db(db_location, university_name):
    chroma_client = chromadb.PersistentClient(path=f"{db_location}")
    chroma_client.delete_collection(name=university_name)
    

def list_chroma_collections(db_location):
    chroma_client = chromadb.PersistentClient(path=db_location)
    return chroma_client.list_collections()

print(list_chroma_collections("/Users/lukepitstick/university-search/chroma_langchain_db"))