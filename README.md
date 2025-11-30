# Overview
The goal is to create a search engine for any university website using RAG. This is becuase university websites are often large and complex, and traditional search engines like Google are not able to handle them. The program will start with a couple of universities and then be expanded to include more as time goes on. The final goal is to have a search engine that can handle any university website and provide the most relevant information based on the query while also making sure it uses less energy and water than a google search.

# Features
- [ ] Scrape the university website
- [ ] Extract the text from the website
- [ ] Embed the text
- [ ] Store the text in a vector database
- [ ] Search the vector database
- [ ] Return the most relevant information

# Technologies
- [ ] Scrapy
- [ ] Langchain
- [ ] Chroma
- [ ] Ollama
- [ ] Redis

# Setup
1. Install the dependencies
```bash
pip install -r requirements.txt
```
2. Run the crawler
```bash
python start_crawlers.py --config crawler_config.json
```
3. Run the search engine
```bash
python search_engine.py
```

# Usage
1. Enter the query
2. The search engine will return the most relevant information