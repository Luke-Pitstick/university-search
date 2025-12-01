import streamlit as st
import subprocess
import os
import time
import chromadb
import pandas as pd
from utils.redis_utils import clear_redis
from utils.chroma_utils import clear_chroma_db

# Configuration
LOG_FILE = "/Users/lukepitstick/university-search/crawler_output.log"
CHROMA_DB_PATH = '../../chroma_langchain_db'

st.set_page_config(page_title="University Crawler Dashboard", layout="wide")
st.title("🎓 University Crawler Dashboard")

# ============ Helper Functions ============

def stop_crawler():
    os.system("pkill -f 'start_crawlers.py'")

def check_crawler_running():
    """Check if any crawler process is currently running"""
    result = subprocess.run(['pgrep', '-f', 'start_crawlers.py'], capture_output=True)
    return result.returncode == 0

def read_log_file(max_lines=100):
    """Read the last N lines from the log file"""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
            return ''.join(lines[-max_lines:])
    return ""

def clear_log_file():
    """Clear the log file"""
    with open(LOG_FILE, 'w') as f:
        f.write("")

@st.cache_resource
def get_chroma_client():
    if not os.path.exists(CHROMA_DB_PATH):
        return None
    return chromadb.PersistentClient(path=CHROMA_DB_PATH)

# ============ Tabs ============

tab1, tab2, tab3 = st.tabs(["🕷️ Crawler", "🗄️ Database Inspector", "🔧 Utils"])

# ============ Tab 1: Crawler ============

with tab1:
    st.header("Crawler Control")
    
    url = st.text_input("URL to crawl", value="https://www.colorado.edu")
    
    col_a, col_b = st.columns(2)
    with col_a:
        count = st.number_input("Number of crawlers", value=1, min_value=1, max_value=10)
    with col_b:
        test_mode = st.checkbox("Test mode", value=False)
    
    config_path = st.text_input("Config file path", value="/Users/lukepitstick/university-search/crawler_config.json")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ Start Crawler", use_container_width=True):
            clear_log_file()
            with open(LOG_FILE, 'w') as log_file:
                process = subprocess.Popen(
                    ['python', '-u', '/Users/lukepitstick/university-search/src/crawler/start_crawlers.py', url, str(count), config_path, str(test_mode)],
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                )
            st.success(f"Crawler started with PID: {process.pid}")
            time.sleep(1)
            st.rerun()
    
    with col2:
        if st.button("⏹️ Stop Crawler", use_container_width=True):
            stop_crawler()
            st.warning("Crawler stopped")
            st.rerun()
    
    with col3:
        if st.button("🗑️ Clear Log", use_container_width=True):
            clear_log_file()
            st.rerun()
    
    # Status
    is_running = check_crawler_running()
    if is_running:
        st.info("🕷️ Crawler is currently running...")
    else:
        st.write("No crawler running")
    
    # Log output
    st.subheader("Output Log")
    log_content = read_log_file()
    if log_content:
        st.code(log_content, language="text")
    else:
        st.write("_No output yet_")
    
    # Auto-refresh while running
    if is_running:
        time.sleep(2)
        st.rerun()

# ============ Tab 2: Database Inspector ============

with tab2:
    st.header("ChromaDB Inspector")
    
    client = get_chroma_client()
    
    if not client:
        st.error(f"Database path not found: {CHROMA_DB_PATH}")
    else:
        try:
            collections = client.list_collections()
            collection_names = [c.name for c in collections]
            
            if not collection_names:
                st.warning("No collections found in the database.")
            else:
                selected_collection = st.selectbox("Select Collection", collection_names)
                
                if selected_collection:
                    collection = client.get_collection(selected_collection)
                    count = collection.count()
                    st.metric("Total Documents", count)
                    
                    # Search section
                    st.subheader("Search / Explore")
                    query_text = st.text_input("Search query (leave empty to browse)")
                    limit = st.slider("Limit results", 1, 50, 10)
                    
                    results = None
                    if query_text:
                        results = collection.query(
                            query_texts=[query_text],
                            n_results=limit
                        )
                    else:
                        results = collection.get(limit=limit)
                    
                    if results:
                        # Format results
                        if query_text:
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
                            idx = ids.index(selected_id)
                            
                            col1, col2 = st.columns([1, 2])
                            with col1:
                                st.json(metadatas[idx])
                            with col2:
                                st.text_area("Full Content", documents[idx], height=400)
        
        except Exception as e:
            st.error(f"Error accessing ChromaDB: {str(e)}")

# ============ Tab 3: Utils ============

with tab3:
    st.header("Utilities")
    
    st.subheader("Redis")
    redis_url = st.text_input("Redis URL", value="redis://localhost:6379")
    if st.button("🗑️ Clear Redis", use_container_width=True):
        clear_redis(redis_url)
        st.success("Redis cleared!")
    
    st.divider()
    
    st.subheader("ChromaDB")
    chroma_path = st.text_input("Chroma DB Path", value="chroma_langchain_db/")
    collection_to_clear = st.text_input("Collection name to clear", value="university_pages")
    if st.button("🗑️ Clear Chroma Collection", use_container_width=True):
        clear_chroma_db(chroma_path, collection_to_clear)
        st.success(f"Collection '{collection_to_clear}' cleared!")
        st.cache_resource.clear()  # Clear cached chroma client

