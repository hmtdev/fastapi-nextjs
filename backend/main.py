from fastapi import FastAPI
from app.routes import test

def create_app():
    app = FastAPI(
    title="Demo App",
    version="1.0",
    description="Oke"
)   

    app.include_router(test.route)

    return app