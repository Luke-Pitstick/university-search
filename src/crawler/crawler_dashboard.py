import streamlit as st
import subprocess
import os
import time
from utils.redis_utils import clear_redis
from utils.chroma_utils import clear_chroma_db

LOG_FILE = "/Users/lukepitstick/university-search/crawler_output.log"

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

st.title("Crawler Dashboard")

st.write("This is a dashboard for the crawler")

url = st.text_input("Enter the URL to crawl", value="https://www.colorado.edu")
count = st.number_input("Enter the number of crawlers", value=1, min_value=1, max_value=10)
config_path = st.text_input("Enter the path to the config file", value="/Users/lukepitstick/university-search/crawler_config.json")
test_mode = st.checkbox("Test mode", value=False)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Start Crawler(s)"):
        # Clear log file for fresh start
        clear_log_file()
        # Start process with output redirected to log file
        with open(LOG_FILE, 'w') as log_file:
            process = subprocess.Popen(
                ['python', '-u', '/Users/lukepitstick/university-search/src/crawler/start_crawlers.py', url, str(count), config_path, str(test_mode)],
                stdout=log_file,
                stderr=subprocess.STDOUT,
            )
        st.success(f"Crawler started with PID: {process.pid}")
        time.sleep(1)  # Give it a moment to start
        st.rerun()

with col2:
    if st.button("Stop Crawler(s)"):
        stop_crawler()
        st.warning("Crawler stopped")
        st.rerun()

with col3:
    if st.button("Clear Log"):
        clear_log_file()
        st.rerun()

# Show crawler status
is_running = check_crawler_running()
if is_running:
    st.info("🕷️ Crawler is currently running...")
else:
    st.write("No crawler running")

# Show log output
st.subheader("Output Log")
log_content = read_log_file()
if log_content:
    st.code(log_content, language="text")
else:
    st.write("_No output yet_")

# Auto-refresh while crawler is running
if is_running:
    time.sleep(2)
    st.rerun()
    

    
st.write("Utils")
    
if st.button("Clear Redis"):
    clear_redis("redis://localhost:6379")
    

chroma_db_path = st.text_input("Enter the path to the Chroma DB", value="chroma_langchain_db/")
collection_name = st.text_input("Enter the name of the collection", value="colorado")
    
if st.button("Clear Chroma DB"):
    clear_chroma_db(chroma_db_path, collection_name)