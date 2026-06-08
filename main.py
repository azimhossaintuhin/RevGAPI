import pkgutil
import importlib
from fastapi import FastAPI
from  src.config.database import async_engine, get_session ,Base
from contextlib import asynccontextmanager
from src.routers import User_Routers
from  fastapi.staticfiles import StaticFiles
from src.core.file_handler import IMAGE_UPLOAD_FOLDER
from src.events import load_events

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_events()
    yield





app = FastAPI(lifespan=lifespan)

app.include_router(User_Routers.router)

app.mount("/media", StaticFiles(directory=IMAGE_UPLOAD_FOLDER), name="media")

@app.get("/")
async def root():
    return {"message": "Hello World"}