# app.bot.init
import logging
import time

from telegram.error import NetworkError
from telegram.ext import (
    Application,
    ApplicationBuilder,
    ContextTypes,
)

from app.bot.context import DatabaseContext
from app.config import Config
from app.database import Database

from .handlers import register_handlers

logger = logging.getLogger(__name__)


# Telegram Bot Class
class TelegramBot:
    def __init__(self):
        self.bot = self.Bot()
        self.db = self.bot.db
        self.app = self.bot.app

    class Bot:
        def __init__(self):
            self.db = Database()
            self.app: Application = (
                ApplicationBuilder()
                .token(Config.TELEGRAM_TOKEN)
                .context_types(ContextTypes(context=DatabaseContext))
                .build()
            )
            register_handlers(self.app)

    async def start(self, delay_attempts: int = 2):
        while True:
            try:
                # Initialize database
                await self.db.init()
                logger.info("🗃️ Database initialized")

                # Initialize the application
                await self.app.initialize()
                logger.info("🤖 Bot application initialized")

                # Delete any existing webhook
                await self.app.bot.delete_webhook(drop_pending_updates=True)

                logger.info("⛱ Opening connection path")
                logger.info("🏁 Starting bot polling...")

                await self.app.start()
                await self.app.updater.start_polling(
                    allowed_updates=["message", "callback_query", "inline_query"]
                )

                logger.info("🚀 Bot successfully started.")
                break

            except NetworkError:
                logger.error("Everything works fine… except you're in Iran!")
                time.sleep(delay_attempts)

            except Exception as e:
                logger.error(f"Failed to start bot: {str(e)}")
                raise
