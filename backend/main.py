from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.database.database import create_db_and_tables
from fastapi.middleware.cors import CORSMiddleware
from app.routes import api_v1
from fastapi import FastAPI
from fastapi.responses import RedirectResponse


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
## Add middleware 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "Accept"]
)
app.include_router(api_v1.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return RedirectResponse(url="/docs")