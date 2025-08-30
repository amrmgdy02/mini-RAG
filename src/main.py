from fastapi import FastAPI
from routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from stores.llms.LLMFactory import LLMFactory
from stores.VectorDB.VectorDBFactory import VectorDBFactory

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    settings = get_settings()
    app.mongodb_client = AsyncIOMotorClient(settings.MONGO_URL)
    app.mongodb_connection = app.mongodb_client[settings.MONGODB_NAME]
    
    LLM_factory = LLMFactory(config=settings)
    generation_llm = LLM_factory.create(settings.LLM_PROVIDER)
    embedding_llm = LLM_factory.create(settings.LLM_PROVIDER)

    generation_llm.set_generation_model(model_id=settings.GENERATION_MODEL_ID)
    embedding_llm.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID, embedding_size=settings.EMBEDDING_SIZE)
    
    vectordb_factory = VectorDBFactory(settings)
    vector_db_client = vectordb_factory.create("QDRANT")


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

app.include_router(base.base_router)
app.include_router(data.data_router)

