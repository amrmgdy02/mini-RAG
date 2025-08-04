from fastapi import FastAPI, APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers.DataController import DataController

data_router = APIRouter(
    prefix="/api/v1",
    tags=["api/v1", "data"]
)

@data_router.post("/upload")
async def upload_file(file: UploadFile, app_settings: Settings = Depends(get_settings)):
    
    # Validate file
    isValidFile, res_signal = DataController().validate_file(file)
    if not isValidFile:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": res_signal.value}
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "File processed successfully", "filename": file.filename}
        )
