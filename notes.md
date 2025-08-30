##QdrantClient in Python
#The QdrantClient Python class can connect to Qdrant in two modes:

Local mode: QdrantClient(path="...") (single-process, direct file access, no concurrency)
Server mode: QdrantClient(host="localhost", port=6333) (network access, supports concurrency)
When you use host and port, the client sends HTTP requests to the Qdrant server’s REST API.