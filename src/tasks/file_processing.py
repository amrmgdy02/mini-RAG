from celery_app import celery_app, get_setup
from models.ProjectModel import ProjectModel
import asyncio
import logging
from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from helpers.config import get_settings, Settings
from controllers.DataController import DataController
from controllers.ProcessFileController import ProcessFileController
from controllers.VectorStoreController import VectorStoreController
from models import ResponseSignal
import aiofiles
import logging
from models.ProjectModel import ProjectModel
from models.DataChunkModel import DataChunkModel
from models.db_schemes.project import Project
from models.db_schemes.DataChunk import DataChunk
from typing import List

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, 
                 name='tasks.file_processing.chunk_file')
def chunk_file(self, project_id, filename: str,
               chunk_size: int = 100,
               overlap: int = 20):
    
    return asyncio.run(
        _chunk_file(self, project_id, filename, chunk_size,
                     overlap)
    )
    
async def _chunk_file(task_instance, project_id,
                        filename: str,
                        chunk_size: int = 100,
                        overlap: int = 20
                    ):
    
    (
        mongodb_client,
        mongodb_connection,
        generation_llm,
        embedding_llm,
        vector_db_client
    ) = await get_setup()
    
    try:
        db_client = mongodb_client

        file_processor = ProcessFileController(project_id=project_id)
        print("Before get file content")
        file_content = file_processor.get_file_content(filename)
        print("After get file content")
        chunk_size = chunk_size if chunk_size else 100
        overlap = overlap if overlap else 20
        
        project_model = await ProjectModel.create_instance(db_client=db_client)
        project = await project_model.find_project_or_create_one(
            project_id=project_id
        )
        
        if not project.id:
            logger.error("Project ID is None - cannot create chunks")
            return {
                "signal": ResponseSignal.FILE_PROCESS_FAILED.value,
                "error": "Project ID is None"
            }
        print("file content: ", file_content)
        file_chunks = file_processor.process_file_into_chunks(project_id, file_content, chunk_size, overlap)
        print("file chunks: ", file_chunks)
        if not file_chunks or len(file_chunks) == 0:
            return {
                "signal": ResponseSignal.FILE_PROCESS_FAILED.value
            }
            
        file_chunks = [
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
            )
            for i, chunk in enumerate(file_chunks)
        ]
        
        data_chunk_model = await DataChunkModel.create_instance(db_client=db_client)
        num_inserted = await data_chunk_model.insert_many_chunks(file_chunks)
        
        embed_chunks.delay([chunk.model_dump(by_alias=True, exclude_unset=True) for chunk in file_chunks])
            
        return {
            "signal": ResponseSignal.FILE_PROCESS_SUCCESS.value,
            "inserted_chunks": num_inserted
        }
    
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        return {
            "signal": ResponseSignal.FILE_PROCESS_FAILED.value,
            "error": str(e)
        }


@celery_app.task(bind=True,
                 name='tasks.file_processing.embed_chunks')
def embed_chunks(self, chunks: List[DataChunk]):
    
    return asyncio.run(
        _embed_chunks(self, chunks)
    )
    
async def _embed_chunks(task_instance, chunks:List):
    try:
        (
            mongodb_client,
            mongodb_connection,
            generation_llm,
            embedding_llm,
            vector_db_client
        ) = await get_setup()

        vector_store_controller = VectorStoreController(embedding_llm, vector_db_client)

        for chunk in chunks:
            embeddings = vector_store_controller.embed_chunk(
                    text=chunk['chunk_text'],
                    metadata=chunk['chunk_metadata']
                )

            if not embeddings or len(embeddings) == 0:
                continue
            
        return {
            "signal": ResponseSignal.FILE_PROCESS_SUCCESS.value,
        }
            
    except Exception as e:
        logger.error(f"Error embedding chunk: {e}")
        return {
            "signal": ResponseSignal.FILE_PROCESS_FAILED.value,
            "error": str(e)
        }