import streamlit as st
import chromadb
import pandas as pd
import os

# Configuration
CHROMA_DB_PATH = "/Users/lukepitstick/university-search/chroma_langchain_db/"
COLLECTION_NAME = "university_pages"

st.set_page_config(page_title="ChromaDB Inspector", layout="wide")
st.title("ChromaDB Inspector")

@st.cache_resource
def get_client():
    if not os.path.exists(CHROMA_DB_PATH):
        st.error(f"Database path not found: {CHROMA_DB_PATH}")
        return None
    return chromadb.PersistentClient(path=CHROMA_DB_PATH)

client = get_client()

if client:
    try:
        collections = client.list_collections()
        collection_names = [c.name for c in collections]
        
        if not collection_names:
            st.warning("No collections found in the database.")
        else:
            selected_collection = st.selectbox("Select Collection", collection_names, index=collection_names.index(COLLECTION_NAME) if COLLECTION_NAME in collection_names else 0)
            
            if selected_collection:
                collection = client.get_collection(selected_collection)
                count = collection.count()
                st.metric("Total Documents", count)
                
                # Query/Search section
                st.subheader("Search / Explore")
                query_text = st.text_input("Search query (leave empty to browse recent)")
                limit = st.slider("Limit results", 1, 50, 10)
                
                results = None
                if query_text:
                    results = collection.query(
                        query_texts=[query_text],
                        n_results=limit
                    )
                else:
                    # Just get first N items if no query
                    results = collection.get(limit=limit)
                
                if results:
                    # Format results for display
                    if query_text:
                        # Query results structure
                        ids = results['ids'][0]
                        metadatas = results['metadatas'][0] if results['metadatas'] else [{}] * len(ids)
                        documents = results['documents'][0] if results['documents'] else [""] * len(ids)
                        distances = results['distances'][0] if 'distances' in results and results['distances'] else [0] * len(ids)
                        
                        data = []
                        for i, id_ in enumerate(ids):
                            data.append({
                                "ID": id_,
                                "Distance": distances[i],
                                "Metadata": metadatas[i],
                                "Content": documents[i][:500] + "..." if len(documents[i]) > 500 else documents[i]
                            })
                    else:
                        # Get results structure
                        ids = results['ids']
                        metadatas = results['metadatas'] if results['metadatas'] else [{}] * len(ids)
                        documents = results['documents'] if results['documents'] else [""] * len(ids)
                        
                        data = []
                        for i, id_ in enumerate(ids):
                            data.append({
                                "ID": id_,
                                "Metadata": metadatas[i],
                                "Content": documents[i][:500] + "..." if len(documents[i]) > 500 else documents[i]
                            })
                    
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                    
                    # Detailed view
                    st.subheader("Detailed Item View")
                    selected_id = st.selectbox("Select ID to view full content", ids)
                    if selected_id:
                        # Find the item data
                        idx = ids.index(selected_id)
                        
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.json(metadatas[idx])
                        with col2:
                            st.text_area("Full Content", documents[idx], height=400)

    except Exception as e:
        st.error(f"Error accessing ChromaDB: {str(e)}")

