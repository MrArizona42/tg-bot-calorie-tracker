from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
import httpx

from settings.config import settings

import logging

logger = logging.getLogger(__name__)

FASTAPI_URL = settings.FASTAPI_URL
FOOD_API_KEY = settings.FOOD_API_KEY

router = Router()


class WorkoutLogging(StatesGroup):
    telegram_id = State()
    type = State()
    duration = State()
    calories = State()


async def send_log_workout(workout_data):
    async with httpx.AsyncClient() as client:
        response = await client.post(FASTAPI_URL + "/log_workout", json=workout_data)
        logger.info(f'Response from fast-api: {response.text}')
        if response.status_code == 200:
            message = "The workout has been logged"
        else:
            error_text = response.text
            message = f"Error: {error_text}"

    return message


@router.message(Command("log_workout"))
async def cmd_log_workout(message: Message, state: FSMContext):
    async with httpx.AsyncClient() as client:
        response = await client.get(FASTAPI_URL + f"/check_user_exist/{message.from_user.id}")
        if response.status_code != 200:
            await message.answer("Account is not found. \
                Please try to register your account first using /new_user command")
            await state.clear()
            return

    await state.update_data(telegram_id=message.from_user.id)

    keyboard = InlineKeyboardBuilder()
    workouts = ["Jogging", "Cycling", "Weight Lifting"]
    for workout in workouts:
        keyboard.button(text=workout, callback_data=f"workout_{workout}")

    await message.answer("Choose your workout:", reply_markup=keyboard.as_markup())


@router.callback_query(F.data.startswith("workout_"))
async def workout_selected(callback: CallbackQuery, state: FSMContext):
    """Handle workout type selection."""
    workout_type = callback.data.split("_")[1]
    await state.update_data(type=workout_type)

    await callback.message.answer(f"You chose {workout_type}. Enter the duration in minutes (e.g., 30).")
    await state.set_state(WorkoutLogging.duration)
    await callback.answer()


@router.message(WorkoutLogging.duration)
async def log_duration(message: Message, state: FSMContext):
    """Get workout duration from user input."""
    try:
        duration = int(message.text)
        if duration <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Please enter a valid number of minutes.")
        return
    
    workout_data = await state.get_data()
    w_type = workout_data.get('type')
    if w_type == 'Jogging':
        calories = duration * 10
    elif w_type == 'Cycling':
        calories = duration * 8
    elif w_type == 'Weight Lifting':
        calories = duration * 6

    await state.update_data(duration=duration)
    await state.update_data(calories=calories)

    workout_data = await state.get_data()

    response_message = await send_log_workout(workout_data)
    await message.answer(response_message)

    await state.clear()
