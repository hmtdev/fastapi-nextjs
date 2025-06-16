from fastapi import APIRouter


route = APIRouter(tags=["test"])


@route.get("/")
async def test_endpoint():
    return {"message": "Test endpoint working"}