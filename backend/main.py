from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.database.database import create_db_and_tables
from app.routes import auth
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    # Initialize the database or any other startup tasks here
    yield
    # Cleanup tasks can be done here if needed

settings = get_settings()

app = FastAPI(
    title="Demo App",
    version="1.0",
    description="Oke",
    lifespan=lifespan
)   
app.include_router(auth.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {
        "Environment": settings.environment,
        "Database URL": settings.database_url,
        "Debug Mode": settings.debug,
        "API Key": settings.api_key
    }