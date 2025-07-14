from contextlib import asynccontextmanager
import google.generativeai as genai
from app.core.config import get_settings
from app.database.database import create_db_and_tables
from fastapi.middleware.cors import CORSMiddleware
from app.routes import api_v1
from app.routes.genai import gen_api
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.services.genmini import gemini_service


settings = get_settings()
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Application starting...")
    create_db_and_tables()
    # Initialize the database or any other startup tasks here
    gemini_service.initialize()
    yield
    # Cleanup tasks can be done here if needed
    print("👋 Application shutting down...")


app = FastAPI(
    title="Demo App",
    version="1.0",
    description="Oke",
    lifespan=lifespan
)
## Add middleware 
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost",
        "https://miniature-carnival-p5w4979j4hrqwg-3000.app.github.dev" 
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "Accept"]
)
app.include_router(api_v1.router, prefix="/api/v1")
app.include_router(gen_api.router,prefix="/api/gen")
@app.get("/")
def read_root():
    return RedirectResponse(url="/docs")