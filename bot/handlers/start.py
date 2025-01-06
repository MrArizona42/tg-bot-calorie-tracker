from aiogram import Router, types
from aiogram.filters import Command
import httpx

from settings.config import settings

FASTAPI_URL = settings.FASTAPI_URL

router = Router()


@router.message(Command("start"))
async def start_command(message: types.Message):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FASTAPI_URL}/")
        if response.status_code == 200:
            data = response.json()
            reply_text = f"🚀 FastAPI says: {data['message']}"
        else:
            reply_text = "❌ Failed to reach FastAPI backend."

    await message.answer(reply_text)
