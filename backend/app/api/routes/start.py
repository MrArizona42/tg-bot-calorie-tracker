from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def start():
    message = "Hi there! It's your FastAPI app responding!"
    return {"message": message}
