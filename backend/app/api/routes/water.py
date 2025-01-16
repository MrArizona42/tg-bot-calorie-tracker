from typing import Union

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from db.session import get_db_connection

router = APIRouter()


class Water(BaseModel):
    telegram_id: int
    volume: Union[float, int]


@router.post("/log_water")
async def log_water(water: Water):
    conn = await get_db_connection()
    try:
        await conn.execute(
            """
            INSERT INTO water_log (telegram_id, volume)
            VALUES ($1, $2)
            """,
            water.telegram_id, water.volume
        )
        return {"message": "Water logged successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await conn.close()


@router.get("/check_today_water/{telegram_id}")
async def check_today_water(telegram_id: int):
    conn = await get_db_connection()
    try:
        total_volume = await conn.fetch(
            """
            SELECT SUM(volume) as total_volume
            FROM water_log
            WHERE DATE_TRUNC('day', event_time) = DATE_TRUNC('day', now())
                AND telegram_id = $1
            """,
            telegram_id
        )
        total_volume = total_volume[0].get('total_volume')

        result = {
            'total_volume': total_volume
        }

        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await conn.close()
