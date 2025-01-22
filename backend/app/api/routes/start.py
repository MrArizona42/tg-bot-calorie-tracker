from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from db.session import get_db_connection

router = APIRouter()


class WelcomeResponse(BaseModel):
    message: str


@router.get("/", response_model=WelcomeResponse)
async def start():
    conn = await get_db_connection()
    try:
        check_request = await conn.fetch(
            "SELECT NOW()::date AS current_date"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await conn.close()

    message = "Hi there!\n"
    message += f"Today is {check_request[0]['current_date']}, FastAPI and DB are healthy!"
    return {"message": message}
