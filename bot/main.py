import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from settings.config import settings
from handlers.start import router as start_router
from handlers.new_user import router as new_user_router
from handlers.delete_user import router as delete_user_router
from handlers.log_food import router as log_food_router
from handlers.summmary import router as check_today_intake_router
from middleware.logger import LoggingMiddleware

logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

dp.update.middleware(LoggingMiddleware())

dp.include_router(start_router)
dp.include_router(new_user_router)
dp.include_router(delete_user_router)
dp.include_router(log_food_router)
dp.include_router(check_today_intake_router)


async def setup_bot_commands():
    bot_commands = [
        BotCommand(command="/start", description="Welcome message, check connection"),
        BotCommand(command="/new_user", description="Register a new user"),
        BotCommand(command="/delete_user", description="Delete user"),
        BotCommand(command="/log_food", description="Log food"),
        BotCommand(command="/check_today_intake", description="Calories that you've eaten today")
    ]
    await bot.set_my_commands(bot_commands)


dp.startup.register(setup_bot_commands)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
