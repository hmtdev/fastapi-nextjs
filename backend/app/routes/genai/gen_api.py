from fastapi import APIRouter, Depends, HTTPException
from app.routes.v1 import auth
from app.services.genmini import GeminiService,get_gemini_service


router = APIRouter(tags=['Genmini'])

@router.get("/correct")
async def correct_text(
    text,
    genmini : GeminiService= Depends(get_gemini_service)
):
    try:
        corrected = await genmini.correct_text(text)
        return corrected
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error correcting text: {str(e)}")