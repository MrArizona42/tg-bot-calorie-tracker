from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from db.session import get_db_connection

router = APIRouter()


class CheckUserExist(BaseModel):
    telegram_id: int


class UserCreate(BaseModel):
    telegram_id: int
    name: str
    age: int
    weight: float
    city: str
    target_active_minutes_per_day: int
    target_calories_per_day: int


@router.post("/check_user_exist")
async def check_user_exist(user: CheckUserExist):
    conn = await get_db_connection()
    try:
        user_data = await conn.fetch(
            f"""
            SELECT *
            FROM users
            WHERE telegram_id = {user.telegram_id}
            """
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await conn.close()
    
    if len(user_data) > 0:
        return Response(status_code=200)
    else:
        raise HTTPException(status_code=404, detail="User not found")


@router.post("/register_user")
async def create_user(user: UserCreate):
    conn = await get_db_connection()
    try:
        await conn.execute(
            """
            INSERT INTO users (telegram_id, name, age, weight, city, target_active_minutes_per_day, target_calories_per_day)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            user.telegram_id, user.name, user.age, user.weight, user.city,
            user.target_active_minutes_per_day, user.target_calories_per_day
        )
        return {"message": "User created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await conn.close()


@router.delete("/delete_user/{telegram_id}")
async def delete_user(telegram_id: int):
    conn = await get_db_connection()
    try:
        result = await conn.execute(
            "DELETE FROM users WHERE telegram_id = $1", telegram_id
        )

        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="User not found")

        return {"message": "User deleted successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    finally:
        await conn.close()