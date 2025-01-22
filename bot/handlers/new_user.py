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
    height = State()
    city = State()
    target_active_minutes_per_day = State()
    target_calories_per_day = State()


@router.message(Command("new_user"))
async def cmd_new_user(message: Message, state: FSMContext):
    async with httpx.AsyncClient() as client:
        response = await client.get(FASTAPI_URL + f"/check_user_exist/{message.from_user.id}")
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
    except ValueError:
        await message.answer("Please enter a valid weight.")
        return

    await message.answer("Enter your height in centimeters:")
    await state.set_state(UserRegistration.height)


@router.message(UserRegistration.height)
async def process_height(message: Message, state: FSMContext):
    try:
        height = float(message.text)
        await state.update_data(height=height)
    except ValueError:
        await message.answer("Please enter a valid height.")
        return

    await message.answer("Enter your city (for weather tracking):")
    await state.set_state(UserRegistration.city)


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

    user_data = await state.get_data()

    base_calories = 10 * user_data['weight'] + 6.25 * user_data['height'] - 5 * user_data['age']
    workout_calories = (6 * user_data['target_active_minutes_per_day'], 10 * user_data['target_active_minutes_per_day'])
    total_min = base_calories + workout_calories[0]
    total_max = base_calories + workout_calories[1]

    message_text = "What's your daily calorie intake target?\n"
    message_text += f'Your base consumption is recommended to be: {base_calories} kcal\n'
    message_text += f'Plus, you are going to spend {workout_calories[0]} - {workout_calories[1]} kcal on workouts\n'
    message_text += f'So, the total recommended calories intake amount is: {total_min} - {total_max} kcal'
    await message.answer(message_text)
    await state.set_state(UserRegistration.target_calories_per_day)


@router.message(UserRegistration.target_calories_per_day)
async def process_calories(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Please enter a valid number.")
        return
    await state.update_data(target_calories_per_day=int(message.text))

    user_data = await state.get_data()

    message_text = 'Your data:\n'

    for key, value in user_data.items():
        message_text += f'{key}: {value}\n'

    await message.answer(message_text)

    async with httpx.AsyncClient() as client:
        response = await client.post(FASTAPI_URL + "/register_user", json=user_data)
        if response.status_code == 200:
            await message.answer("User registered successfully!")
        else:
            error_text = response.text
            await message.answer(f"Error: {error_text}")

    await state.clear()
