# app/bot/init.py

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, Application, ContextTypes
from app.bot.handlers import start_handler, help_handler, bio_handler, echo, tokens_handler
from telegram import Update
from app.config import Config
from app.database import Database
from app.bot.context import DatabaseContext
import logging

logger = logging.getLogger(__name__)

# Telegram Bot
class TelegramBot:
    def __init__(self):
        self.db = Database()
        self.app: Application = (
            ApplicationBuilder()
            .token(Config.TELEGRAM_TOKEN)
            .context_types(ContextTypes(context=DatabaseContext))
            .build()
        )
        
        self.app.add_handler(CommandHandler("start", start_handler))
        self.app.add_handler(CommandHandler("help", help_handler))
        self.app.add_handler(CommandHandler("bio", bio_handler))
        self.app.add_handler(CommandHandler("tokens", tokens_handler)) # new one
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    async def start(self):
        try:
            # Initialize database
            await self.db.init()
            logger.info("Database initialized")
            
            # Initialize the application first
            await self.app.initialize()
            logger.info("Bot application initialized")
            
            # Delete any existing webhook
            await self.app.bot.delete_webhook(drop_pending_updates=True)
            logger.info("Deleted existing webhook")
            
            # Start polling for updates
            logger.info("Starting bot polling...")
            await self.app.start()
            await self.app.updater.start_polling(allowed_updates=['message', 'callback_query'])
            
            logger.info("Bot startup complete")

        except Exception as e:
            logger.error(f"Failed to start bot: {str(e)}")
            raise