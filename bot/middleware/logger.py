import logging
from aiogram import types, BaseMiddleware
from typing import Callable, Dict, Any, Awaitable

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[types.Update, Dict[str, Any]], Awaitable[Any]],
        event: types.Update,
        data: Dict[str, Any]
    ) -> Any:
        """Middleware to log incoming updates"""
        logger.info(f"Received update: {event}")
        try:
            return await handler(event, data)
        except Exception as e:
            logger.error(f"Error processing update: {e}", exc_info=True)
            raise
