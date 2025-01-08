import json
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import httpx

from settings.config import settings

FASTAPI_URL = settings.FASTAPI_URL

router = Router()


class UserRegistration(StatesGroup):
    telegram_id = State()
    name = State()
    age = State()
    weight = State()
    city = State()
    target_active_minutes_per_day = State()
    target_calories_per_day = State()


@router.message(Command("new_user"))
async def cmd_new_user(message: Message, state: FSMContext):
    async with httpx.AsyncClient() as client:
        user_data = {"telegram_id": message.from_user.id}
        response = await client.post(FASTAPI_URL + "/check_user_exist", json=user_data)
        if response.status_code == 200:
            await message.answer("This account has already been registered.")
            await state.clear()
            return

    await state.update_data(telegram_id=message.from_user.id)
    await message.answer("What's your name?")
    await state.set_state(UserRegistration.name)


@router.message(UserRegistration.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("How old are you?")
    await state.set_state(UserRegistration.age)


@router.message(UserRegistration.age)
async def process_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Please enter a valid age.")
        return
    await state.update_data(age=int(message.text))
    await message.answer("What's your weight (kg)?")
    await state.set_state(UserRegistration.weight)


@router.message(UserRegistration.weight)
async def process_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text)
        await state.update_data(weight=weight)
        await message.answer("Enter your city (for weather tracking):")
        await state.set_state(UserRegistration.city)
    except ValueError:
        await message.answer("Please enter a valid weight.")


@router.message(UserRegistration.city)
async def process_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("What's your target active minutes per day?")
    await state.set_state(UserRegistration.target_active_minutes_per_day)


@router.message(UserRegistration.target_active_minutes_per_day)
async def process_target_minutes(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Please enter a valid number.")
        return
    await state.update_data(target_active_minutes_per_day=int(message.text))
    await message.answer("What's your daily calorie intake target?")
    await state.set_state(UserRegistration.target_calories_per_day)


@router.message(UserRegistration.target_calories_per_day)
async def process_calories(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Please enter a valid number.")
        return
    await state.update_data(target_calories_per_day=int(message.text))

    user_data = await state.get_data()

    await message.answer(f"Your data: {user_data}")

    async with httpx.AsyncClient() as client:
        response = await client.post(FASTAPI_URL + "/register_user", json=user_data)
        if response.status_code == 200:
            await message.answer("User registered successfully!")
        else:
            error_text = response.text
            await message.answer(f"Error: {error_text}")

    await state.clear()
