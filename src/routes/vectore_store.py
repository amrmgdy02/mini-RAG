from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from controllers.VectorStoreController import VectorStoreController
from stores.llms.LLMFactory import LLMFactory
from fastapi.responses import JSONResponse
from models import ResponseSignal
import logging

logger = logging.getLogger('uvicorn.error')

vector_store_router = APIRouter(
    prefix="/api/v1",
    tags=["api/v1", "vector database"]
)

@vector_store_router.post("/answer-query/{project_id}")
async def answer_query(fastApiRequest: Request, project_id: str, request: dict):
    try:
        vector_store_controller = VectorStoreController(fastApiRequest.app.embedding_llm, fastApiRequest.app.generation_llm, fastApiRequest.app.vector_db_client)
        
        response = vector_store_controller.answer_with_rag(
                project_id=project_id, 
                query=request['query_text'], 
                top_k=request.get('top_k', 5)
            )
        
        return JSONResponse(
            content={
                "signal": "query answer succeeded",
                "response": response
            }
        )

    except Exception as e:
        logger.error(f"Error answering query: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "signal": "query answer failed",
                "error": str(e)
            }
        )

@vector_store_router.post("/query-search/{project_id}")
async def search_query(fastApiRequest: Request, project_id: str, request: dict):
    try:
        vector_store_controller = VectorStoreController(fastApiRequest.app.embedding_llm, fastApiRequest.app.generation_llm, fastApiRequest.app.vector_db_client)

        search_results = vector_store_controller.search_similar_vectors(
                project_id=project_id, 
                query_text=request['query_text'], 
                top_k=request.get('top_k', 5)
            )

        return JSONResponse(
            content={
                "signal": "query search succeeded",
                "results": search_results
            }
        )
        
    except Exception as e:
        logger.error(f"Error searching query: {e}")
        return JSONResponse(
            content={
                "signal": "query search failed",
                "error": str(e)
            }
        )
            
    except Exception as e:
        logger.error(f"Error searching query: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "signal": "query search failed",
                "error": str(e)
            }
        )

# Not used here - automated by celery after file upload
@vector_store_router.post("/embed-vector/{project_id}")
async def embed_chunk(fastApiRequest: Request, project_id: str, request: dict):
    try:
        vecto_store_controller = VectorStoreController(fastApiRequest.app.LLM, fastApiRequest.app.generation_llm, fastApiRequest.app.vectore_db_client)

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
        