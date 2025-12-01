from llm.normal_search import NormalSearch

def test_normal_search():
    normal_search = NormalSearch(chroma_db_path="../../../chroma_langchain_db", university_name="colorado")
    result = normal_search.query("What are academics like at Colorado?")
    print(result)
    
if __name__ == "__main__":
    test_normal_search()