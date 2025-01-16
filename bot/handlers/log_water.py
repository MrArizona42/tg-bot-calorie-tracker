from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import httpx

from settings.config import settings

import logging

logger = logging.getLogger(__name__)

FASTAPI_URL = settings.FASTAPI_URL
FOOD_API_KEY = settings.FOOD_API_KEY

router = Router()


class WaterLogging(StatesGroup):
    telegram_id = State()
    volume = State()


async def send_log_water(water_data):
    async with httpx.AsyncClient() as client:
        response = await client.post(FASTAPI_URL + "/log_water", json=water_data)
        logger.info(f'Response from fast-api: {response.text}')
        if response.status_code == 200:
            message = f"The water has been logged: {water_data.get('volume')}"
        else:
            error_text = response.text
            message = f"Error: {error_text}"

    return message


@router.message(Command("log_water"))
async def cmd_log_water(message: Message, state: FSMContext):
    async with httpx.AsyncClient() as client:
        response = await client.get(FASTAPI_URL + f"/check_user_exist/{message.from_user.id}")
        if response.status_code != 200:
            await message.answer("Account is not found. \
                Please try to register your account first using /new_user command")
            await state.clear()
            return

    await state.update_data(telegram_id=message.from_user.id)

    await message.answer("How much water did you drink? Enter the volume in ml")

    await state.set_state(WaterLogging.volume)


@router.message(WaterLogging.volume)
async def process_water_volume(message: Message, state: FSMContext):
    volume = float(message.text.strip())
    await state.update_data(volume=volume)

    water_data = await state.get_data()
    message_text = await send_log_water(water_data)
    await message.answer(message_text)

    await state.clear()
