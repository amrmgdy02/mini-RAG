from fastapi import FastAPI, APIRouter
from helpers.config import get_settings

base_router = APIRouter(
    prefix="/api/v1",
    tags=["base"]
)

@base_router.get("/")
async def welcome():
    settings = get_settings()
    app_name = settings.APPLICATION_NAME
    app_version = settings.APPLICATION_VERSION
    return {
            "App Name": app_name,
            "Version": app_version,
            }