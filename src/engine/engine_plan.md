# Engine Plan

## Components

### Semantic Caching
If the cosine similarity of the query and the cached content is greater than 0.8, then the cached content is returned.
### Hybrid Search
Will use BM25 and Dense Vector Search to search the database.
### Reranking and Compression
Will use a CrossEncoder to rerank the results and compress the results into to smaller text chunks.
### LLM
Will use an SLM that is 7 to 13 billion parameters for speed and accuracy.
