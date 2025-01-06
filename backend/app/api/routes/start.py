from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class WelcomeResponse(BaseModel):
    message: str


@router.get("/", response_model=WelcomeResponse)
async def start():
    message = "Hi there! It's your FastAPI app responding!"
    return {"message": message}
