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
WEATHER_API_KEY = settings.WEATHER_API_KEY

router = Router()


class WorkoutLogging(StatesGroup):
    telegram_id = State()
    type = State()
    duration = State()
    calories = State()
    temperature = State()
    water_spent = State()


async def get_weather(city, token):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": token,
        "units": "metric"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(base_url, params=params)

    return response


async def send_log_workout(workout_data):
    async with httpx.AsyncClient() as client:
        response = await client.post(FASTAPI_URL + "/log_workout", json=workout_data)
        logger.info(f'Response from fast-api: {response.text}')
        if response.status_code == 200:
            message = "The workout has been logged\n"
            message += f"You spent about {workout_data['water_spent']} ml of water. "
            message += "Time to restore your water balance!\n"
            message += f"Also, you've burned {workout_data['calories']} kcal. Nicely done!"
        else:
            error_text = response.text
            message = f"Error: {error_text}"

    return message


@router.message(Command("log_workout"))
async def cmd_log_workout(message: Message, state: FSMContext):
    # Check if the user exists
    async with httpx.AsyncClient() as client:
        response = await client.get(FASTAPI_URL + f"/check_user_exist/{message.from_user.id}")
        if response.status_code != 200:
            await message.answer("Account is not found. \
                Please try to register your account first using /new_user command")
            await state.clear()
            return
        else:
            city = response.json()['city']

    # Check temperature if possible
    response = await get_weather(city=city, token=WEATHER_API_KEY)
    if response.status_code == 200:
        temperature = response.json()['main']['temp']
    else:
        temperature = None

    await state.update_data(telegram_id=message.from_user.id)
    await state.update_data(temperature=temperature)

    # Start workout logging
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
        water_spent = duration * 18
    elif w_type == 'Cycling':
        calories = duration * 8
        water_spent = duration * 14
    elif w_type == 'Weight Lifting':
        calories = duration * 6
        water_spent = duration * 10

    await state.update_data(duration=duration)
    await state.update_data(calories=calories)
    await state.update_data(water_spent=water_spent)

    workout_data = await state.get_data()

    if workout_data['temperature'] is not None:
        response_message = await send_log_workout(workout_data)
        await message.answer(response_message)

        await state.clear()
    else:
        await message.answer("Couldn't get your weather. Please enter the approximate temperature today in Celcius")
        await state.set_state(WorkoutLogging.temperature)


@router.message(WorkoutLogging.temperature)
async def log_temperature(message: Message, state: FSMContext):
    try:
        temperature = float(message.text.strip())
        await state.update_date(temperature=temperature)

        workout_data = await state.get_data()
        if temperature > 25:
            await state.update_data(water_spent=workout_data['water_spent'] * 1.5)
        workout_data = await state.get_data()

        response_message = await send_log_workout(workout_data)
        await message.answer(response_message)

        await state.clear()
    except ValueError:
        await message.answer("⚠️ Please enter a valid number for temperature in Celcius (e.g., `25`).")
