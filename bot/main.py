import asyncio
import logging
from aiogram import Bot, Dispatcher

from settings.config import settings
from handlers.start import router as start_router
from handlers.register_user import router as new_user_router
from middleware.logger import LoggingMiddleware

logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

dp.update.middleware(LoggingMiddleware())

dp.include_router(start_router)
dp.include_router(new_user_router)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
