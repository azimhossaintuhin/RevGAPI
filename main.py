from fastapi import FastAPI
from  src.config.database import async_engine, get_session ,Base
from contextlib import asynccontextmanager
from src.routers import User_Routers
from  fastapi.staticfiles import StaticFiles
from src.core.file_handler import IMAGE_UPLOAD_FOLDER




@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.models.users import User, ApiKey
    async  with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Database created")
    yield
    print("Database disposed")
    await async_engine.dispose()
    print("Database disposed")

app = FastAPI(lifespan=lifespan)

app.include_router(User_Routers.router)

app.mount("/media", StaticFiles(directory=IMAGE_UPLOAD_FOLDER), name="media")

@app.get("/")
async def root():
    return {"message": "Hello World"}