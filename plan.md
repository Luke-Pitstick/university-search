# Plan for implementation of university search

## Overview

The goal is to create a search engine for any university website using RAG. This is becuase university websites are often large and complex, and traditional search engines like Google are not able to handle them. The program will start with a couple of universities and then be expanded to include more as time goes on. The final goal is to have a search engine that can handle any university website and provide the most relevant information based on the query while also making sure it uses less energy and water than a google search.


## Components

1. Crawler
    a. This is a scrapy crawler that will scrape a website and extract the content of the website. It will be able to crawl
    in parrallel with other crawlers by using a redis db. Will go through the website using BFS because normally website's like these provide most of the useful info within around 10-15 clicks. Addtionally the crawler will only go to .html files and ignore other files like PDFs, images, etc.

2. Pipeline
    a. Data Cleaning
        i. This will clean the data by removing any HTML tags, special characters, and other unwanted characters to decrease the size of the data and make it useful for the RAG model.
    b. Embedding
        i. This will use an embedding model to embed the data into a vector space using a local model.
    c. Vector Database
        i. This will store the embeddings in a chroma vector database.

3. Search Engine
    a. This will use the chroma vector database to search for the most relevant information based on the query combined with a hybrid search algorithm for speed, accuracy, and relevance. Then it will use a small language model to answer the query. With hybrid search and a small language model, acheiving the goal of using less energy and water than a google search is possible.
    b. The search engine will output in markdown format for easy processing by the UI using BAML for formatting.

4. UI
   1. This will be a simple FastAPI app where users will be able to select a university and type in a query. The app will then use the search engine to find the most relevant information and display it in a readable format in additiona to the source of the information. User's might be asked to provide their own api key for the language model to use but TBD. If that doesn't happen then rate limiting will be used to prevent abuse.