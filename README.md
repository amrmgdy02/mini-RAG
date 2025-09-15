# Mini-RAG

**Mini-RAG** is a modular **Retrieval-Augmented Generation (RAG) platform** for intelligent document search, semantic retrieval, and context-aware language model generation.  
It is designed with a microservices architecture, making it scalable, extensible, and production-ready.

---

## ✨ Features

- **Semantic Search**  
  Powered by **Qdrant** vector database for fast, scalable similarity search over embedded document chunks.

- **LLM Integration**  
  Connects to **local LLMs (Ollama)** for both text generation and embeddings.

- **Automated Document Pipeline**  
  - File upload, PDF parsing, text chunking, and embedding.  
  - Handles large document collections efficiently.  

- **Distributed Processing**  
  - **FastAPI** for REST APIs.  
  - **Celery** for background task orchestration.  

- **Microservices Architecture**  
  Orchestrated with **Docker Compose**, including:  
  - MongoDB  
  - Qdrant  
  - RabbitMQ  
  - Redis  

- **Extensible & Configurable**  
  Modular codebase with environment-based configuration for easy customization.

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/mini-rag.git
cd mini-rag
```

### 2. Configure Environment Variables
Set up environment variables in:
- `src/.env`  
- `docker/env/`

### 3. Start Services with Docker Compose
```bash
docker compose -f docker/docker-compose.yaml up -d --build
```

### 4. Run FastAPI & Celery
```bash
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
celery -A celery_app.celery_app worker --loglevel=info
```

---

## 📂 Folder Structure

```
mini-RAG/
│
├── src/                # Application source code
│   ├── assets/         # Uploaded files and processed data
│   ├── controllers/    # Business logic and workflow controllers
│   ├── helpers/        # Configuration and utility functions
│   ├── models/         # Data models and database schemas
│   ├── routes/         # API route definitions
│   ├── schemes/        # Pydantic schemas
│   ├── stores/         # LLM and VectorDB providers
│   ├── tasks/          # Celery background tasks
│   ├── main.py         # FastAPI entrypoint
│   └── celery_app.py   # Celery configuration
│
├── docker/             # Docker Compose setup and service configs
│   ├── docker-compose.yaml
│   ├── env/
│   ├── mongodb/
│   ├── qdrant_data/
│   ├── rabbitmq/
│   └── redis_data/
```

---

## 🛠️ Tech Stack

- **Backend:** FastAPI, Celery  
- **Databases:** MongoDB, Qdrant  
- **Message Broker:** RabbitMQ  
- **Cache/Queue:** Redis  
- **LLMs & Embeddings:** Ollama
- **Containerization:** Docker & Docker Compose  

---

## 📌 Roadmap

- [ ] Add authentication & role-based access control  
- [ ] Web dashboard for document management  
- [ ] Support for additional LLM providers (OpenAI, Anthropic, etc.)
