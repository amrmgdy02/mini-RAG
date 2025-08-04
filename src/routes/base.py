from fastapi import FastAPI, APIRouter, Depends
from helpers.config import get_settings, Settings

base_router = APIRouter(
    prefix="/api/v1",
    tags=["base"]
)

@base_router.get("/")
async def welcome(app_settings: Settings =Depends(get_settings)):
    app_name = app_settings.APPLICATION_NAME
    app_version = app_settings.APPLICATION_VERSION
    
    return {
            "App Name": app_name,
            "Version": app_version,
            }