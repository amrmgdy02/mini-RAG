from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from controllers.VectorStoreController import VectorStoreController
from fastapi.responses import JSONResponse
from models import ResponseSignal
import logging

logger = logging.getLogger('uvicorn.error')

vector_store_router = APIRouter(
    prefix="/api/v1",
    tags=["api/v1", "vector database"]
)

@vector_store_router.post("/embed-vector/{project_id}")
async def embed_chunk(fastApiRequest: Request, project_id: str, request: dict):
    try:
        vecto_store_controller = VectorStoreController(fastApiRequest.app.LLM, fastApiRequest.app.vectore_db_client)
        
        embeddings = vecto_store_controller.embed_chunk(
                text=request['text'], 
                metadata=request['metadata'], 
                project_id=project_id
            )
        
        if embeddings and len(embeddings)>0:
            return JSONResponse(
            content={
                "signal": ResponseSignal.CHUNK_EMBEDDING_SUCCESS.value,
            }
        )
            
    except Exception as e:
        logger.error(f"Error embedding chunk: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "signal": ResponseSignal.CHUNK_EMBEDDING_FAILED.value,
                "error": str(e)
            }
        )
        