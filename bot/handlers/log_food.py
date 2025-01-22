import re

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


class FoodLogging(StatesGroup):
    telegram_id = State()
    food_name = State()  # text
    food_weight = State()  # in grams
    calories = State()


async def get_calories(food_name: str, food_api_key: str) -> float | None:
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={food_name}&api_key={food_api_key}"
    logger.info(f'Handling food name: {food_name}')

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()

            data = response.json()

            if "foods" not in data or not data["foods"]:
                return None

            nutrients = data["foods"][0].get("foodNutrients", [])
            for nutrient in nutrients:
                if nutrient.get("nutrientName") == "Energy":
                    return float(nutrient.get("value"))

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error while fetching food data: {e}")
        except httpx.RequestError as e:
            logger.error(f"Request error while connecting to food API: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in get_calories(): {e}")

    return None


async def send_log_food(food_data):
    async with httpx.AsyncClient() as client:
        response = await client.post(FASTAPI_URL + "/log_food", json=food_data)
        logger.info(f'Response from fast-api: {response.text}')
        if response.status_code == 200:
            message = f"🍎 The {food_data.get('food_name').capitalize()} was {food_data.get('food_weight')} grams "
            message += f"and had {food_data.get('calories')} kcal.\n"
            message += "The food has been logged"
        else:
            error_text = response.text
            message = f"Error: {error_text}"

    return message


@router.message(Command("log_food"))
async def cmd_log_food(message: Message, state: FSMContext):
    async with httpx.AsyncClient() as client:
        response = await client.get(FASTAPI_URL + f"/check_user_exist/{message.from_user.id}")
        if response.status_code != 200:
            await message.answer("Account is not found. \
                Please try to register your account first using /new_user command")
            await state.clear()
            return

    await state.update_data(telegram_id=message.from_user.id)

    await message.answer("What did you eat today? Enter the food name and amount in grams.\n"
                         "For example: 'banana 150'")

    await state.set_state(FoodLogging.food_name)


@router.message(FoodLogging.food_name)
async def process_food_entry(message: Message, state: FSMContext):
    match = re.search(r"(.+)\s+(\d+[.,]?\d*)\D*$", message.text)

    if not match:
        await message.answer(
            "Please enter the food in the format: food_name amount_in_grams\n"
            "Example: 'banana 150'"
        )
        return

    food_name = match.group(1).strip()
    food_weight = float(match.group(2).replace(",", "."))

    calories = await get_calories(food_name, FOOD_API_KEY)

    if calories is not None:
        calories_consumed = calories * food_weight / 100
        await state.update_data(food_name=food_name)
        await state.update_data(food_weight=food_weight)
        await state.update_data(calories=calories_consumed)

        food_data = await state.get_data()

        message_text = await send_log_food(food_data)
        await message.answer(message_text)
        await state.clear()
    else:
        await message.answer(
            f"⚠️ Sorry, I couldn't find calorie data for {food_name}.\n"
            "Please enter the calories manually (kcal per 100g):"
        )
        await state.update_data(food_name=food_name)
        await state.update_data(food_weight=food_weight)

        await state.set_state(FoodLogging.calories)


@router.message(FoodLogging.calories)
async def handle_manual_calories(message: Message, state: FSMContext):
    try:
        calories = float(message.text.strip())
    except ValueError:
        await message.answer("⚠️ Please enter a valid number for calories (e.g., `52`).")

    food_data = await state.get_data()
    food_weight = food_data.get("food_weight")
    calories_consumed = calories * food_weight / 100
    await state.update_data(calories=calories_consumed)

    food_data = await state.get_data()

    message_text = await send_log_food(food_data)
    await message.answer(message_text)
    await state.clear()
