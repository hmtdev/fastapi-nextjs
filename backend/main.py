from fastapi import FastAPI
# from app.routes import test
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Demo App",
    version="1.0",
    description="Oke"
)   

# app.include_router(test.route)

@app.get("/")
def read_root():
    return {
        "Environment": settings.environment,
        "Database URL": settings.database_url,
        "Debug Mode": settings.debug,
        "API Key": settings.api_key
    }