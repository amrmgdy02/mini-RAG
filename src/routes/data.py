from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from helpers.config import get_settings, Settings
from controllers.DataController import DataController
from controllers.ProcessFileController import ProcessFileController
from models import ResponseSignal
import aiofiles
import logging
from .schemes.data import ProcessFileRequest
from models.ProjectModel import ProjectModel
from models.DataChunkModel import DataChunkModel
from models.db_schemes.project import Project
from models.db_schemes.DataChunk import DataChunk


logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1",
    tags=["api/v1", "data"]
)

@data_router.post("/upload/{project_id}")
async def upload_file(project_id: str, file: UploadFile, request: Request, app_settings: Settings = Depends(get_settings)):

    isValidFile, res_signal = DataController().validate_file(file)
    
    if not isValidFile:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": res_signal}
        )
    
    db_client = request.app.mongodb_client
    project_model = await ProjectModel.create_instance(db_client=db_client)
    
    try:
        project = await project_model.find_project_or_create_one(
            project_id=project_id
        )
    except Exception as e:
        logger.error(f"Database error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Database connection failed"}
        )
    
    file_path, unique_filename = DataController().generate_unique_filepath(
        orig_file_name=file.filename,
        project_id=project_id
    )
    
    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:

        logger.error(f"Error while uploading file: {e}")

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )

    return JSONResponse(
            content={
                "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                "filename": unique_filename,
                "project_id": str(project.id) if project.id else "no_id"
            }
        )

@data_router.get("/projects")
async def get_projects(request: Request, page_number: int = 1, page_size: int = 10):
    db_client = request.app.mongodb_client
    project_model = await ProjectModel.create_instance(db_client=db_client)

    try:
        projects, total_pages_num = await project_model.get_all_projects(page_number, page_size)
    except Exception as e:
        logger.error(f"Database error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Database connection failed"}
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "projects": [str(project.id) for project in projects],
            "total_pages": total_pages_num
        }
    )

@data_router.get("/debug/indexes/{project_id}")
async def get_collection_indexes(request: Request, project_id: str = "projects"):
    """Debug endpoint to check what indexes exist on collections"""
    try:
        db_client = request.app.mongodb_client
        project_model = await ProjectModel.create_instance(db_client=db_client)
        
        # Get indexes for projects collection
        project_indexes = await project_model.get_collection_indexes()
        
        # Also check DataChunk indexes if requested
        data_chunk_model = await DataChunkModel.create_instance(db_client=db_client)
        chunk_indexes = await data_chunk_model.get_collection_indexes() if hasattr(data_chunk_model, 'get_collection_indexes') else []
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "project_indexes": project_indexes,
                "chunk_indexes": chunk_indexes,
                "collections": await db_client[project_model.app_settings.MONGODB_NAME].list_collection_names()
            }
        )
        
    except Exception as e:
        logger.error(f"Error checking indexes: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(e)}
        )

@data_router.post("/process/{project_id}")
async def process_file(fastApiRequest: Request, project_id: str, request: ProcessFileRequest):
    
    try:
        db_client = fastApiRequest.app.mongodb_client

        file_processor = ProcessFileController(project_id=project_id)

        file_content = file_processor.get_file_content(request.filename)
        
        chunk_size = request.chunk_size if request.chunk_size else 100
        overlap = request.overlap if request.overlap else 20
        
        project_model = await ProjectModel.create_instance(db_client=db_client)
        project = await project_model.find_project_or_create_one(
            project_id=project_id
        )
        
        if not project.id:
            logger.error("Project ID is None - cannot create chunks")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "signal": ResponseSignal.FILE_PROCESS_FAILED.value,
                    "error": "Project ID is None"
                }
            )
        
        file_chunks = file_processor.process_file_into_chunks(file_content, chunk_size, overlap)
        
        if not file_chunks or len(file_chunks) == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.FILE_PROCESS_FAILED.value
                }
            )
            
        file_chunks = [
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=i+1,
                chunk_project_id=project.id,
            )
            for i, chunk in enumerate(file_chunks)
        ]
        
        data_chunk_model = await DataChunkModel.create_instance(db_client=db_client)
        num_inserted = await data_chunk_model.insert_many_chunks(file_chunks)
            
        return JSONResponse(
            content={
                "signal": ResponseSignal.FILE_PROCESS_SUCCESS.value,
                "inserted_chunks": num_inserted
            }
        )
    
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "signal": ResponseSignal.FILE_PROCESS_FAILED.value,
                "error": str(e)
            }
        )

    
