from fastapi import APIRouter
from app.routes.v1 import auth


router = APIRouter()

router.include_router(auth.router)
