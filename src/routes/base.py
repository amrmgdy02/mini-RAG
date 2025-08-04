from fastapi import FastAPI, APIRouter
import os 

base_router = APIRouter(
    prefix="/api/v1",
    tags=["base"]
)

@base_router.get("/")
async def welcome():
    app_name = os.getenv("APPLICATION_NAME")
    app_version = os.getenv("APPLICATION_VERSION")
    return {
            "App Name": app_name,
            "Version": app_version,
            }