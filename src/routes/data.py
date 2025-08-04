from fastapi import FastAPI, APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from helpers.config import get_settings, Settings
from controllers.DataController import DataController
from controllers.ProcessFileController import ProcessFileController
from models import ResponseSignal
import aiofiles
import logging
from .schemes.data import ProcessFileRequest

from pydantic import BaseModel


logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1",
    tags=["api/v1", "data"]
)

@data_router.post("/upload/{project_id}")
async def upload_file(project_id: str, file: UploadFile, app_settings: Settings = Depends(get_settings)):

    isValidFile, res_signal = DataController().validate_file(file)
    if not isValidFile:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": res_signal}
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
                "filename": unique_filename
            }
        )

@data_router.post("/process/{project_id}")
async def process_file(project_id: str, request: ProcessFileRequest):

    file_processor = ProcessFileController(project_id=project_id)

    file_content = file_processor.get_file_content(request.filename)
    chunk_size = request.chunk_size if request.chunk_size else 100
    overlap = request.overlap if request.overlap else 20
    
    file_chunks = file_processor.process_file_into_chunks(file_content, chunk_size, overlap)
    
    if not file_chunks or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_PROCESS_FAILED.value
            }
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.FILE_PROCESS_SUCCESS.value,
            "file_chunks": [
                {
                    "page_content": chunk.page_content,
                    "metadata": chunk.metadata
                }
                for chunk in file_chunks
            ]
        }
    )

    
