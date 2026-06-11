from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.core.file_handler import IMAGE_UPLOAD_FOLDER
from src.events import load_events
from src.api.v1 import router as api_v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_events()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(api_v1_router)
app.mount("/media", StaticFiles(directory=IMAGE_UPLOAD_FOLDER), name="media")

@app.get("/")
async def root():
    return {"message": "Hello World"}