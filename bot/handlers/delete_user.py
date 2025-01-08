from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import httpx

from settings.config import settings

FASTAPI_URL = settings.FASTAPI_URL

router = Router()


class UserDelete(StatesGroup):
    telegram_id = State()
    confirmation = State()


@router.message(Command("delete_user"))
async def delete_user(message: Message, state: FSMContext):
    async with httpx.AsyncClient() as client:
        user_data = {"telegram_id": message.from_user.id}
        response = await client.post(FASTAPI_URL + "/check_user_exist", json=user_data)
        if response.status_code == 200:
            await message.answer("This action will permanently delete your data. \
                                 Do you wish to continue? Type 'yes', if you agree.")

    await state.update_data(telegram_id=message.from_user.id)
    await state.set_state(UserDelete.confirmation)


@router.message(UserDelete.confirmation)
async def confirm_delete(message: Message, state: FSMContext):
    await state.update_data(confirmation=message.text.lower())
    if message.text.lower() == 'yes':
        async with httpx.AsyncClient() as client:
            response = await client.delete(FASTAPI_URL + f"/delete_user/{message.from_user.id}")
            if response.status_code == 200:
                await message.answer("User has successfully been deleted")
                await state.clear()
                return
            else:
                error_text = response.text
                await message.answer(f"Error: {error_text}")
