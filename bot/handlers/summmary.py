from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import httpx

from settings.config import settings

import logging

logger = logging.getLogger(__name__)

FASTAPI_URL = settings.FASTAPI_URL
FOOD_API_KEY = settings.FOOD_API_KEY

router = Router()


@router.message(Command("check_today_intake"))
async def check_today_intake(message: Message):
    async with httpx.AsyncClient() as client:
        response = await client.get(FASTAPI_URL + f"/check_user_exist/{message.from_user.id}")
        if response.status_code != 200:
            await message.answer("Account is not found. \
                Please try to register your account first using /new_user command")

            return

        else:
            response = await client.get(FASTAPI_URL + f"/check_today_intake/{message.from_user.id}")
            total_calories = response.json().get('total_calories')
            calories_by_food = response.json().get('calories_by_food')

            message_text = f"Your calories intake today: {total_calories}\n"
            for row in calories_by_food:
                message_text += f'{row['food_name']}: {row['calories']}\n'

            await message.answer(message_text)


@router.message(Command("check_today_water"))
async def check_today_water(message: Message):
    async with httpx.AsyncClient() as client:
        response = await client.get(FASTAPI_URL + f"/check_user_exist/{message.from_user.id}")
        if response.status_code != 200:
            await message.answer("Account is not found. \
                Please try to register your account first using /new_user command")

            return

        else:
            response = await client.get(FASTAPI_URL + f"/check_today_water/{message.from_user.id}")
            total_volume = response.json().get('total_volume')

            message_text = f"Your water intake today: {total_volume} ml"

            await message.answer(message_text)


@router.message(Command("check_today_workouts"))
async def check_today_workouts(message: Message):
    async with httpx.AsyncClient() as client:
        response = await client.get(FASTAPI_URL + f"/check_user_exist/{message.from_user.id}")
        if response.status_code != 200:
            await message.answer("Account is not found. \
                Please try to register your account first using /new_user command")

            return

        else:
            response = await client.get(FASTAPI_URL + f"/check_today_workouts/{message.from_user.id}")
            total_time = response.json().get('total_time')
            total_calories = response.json().get('total_calories')

            message_text = f"Your total sport activities today: {total_time} min and {total_calories} cal"

            await message.answer(message_text)
