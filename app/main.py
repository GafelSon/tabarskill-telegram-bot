import logging

from fastapi import FastAPI

from app.bot.init import TelegramBot
from app.config import Config

# Configure logging
Config.setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="TabarSkill Telegram Bot", version="0.1.0")
bot = TelegramBot()


@app.on_event("startup")
async def startup_event():
    try:
        await bot.start()
        logger.info("Bot started successfully.")
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    try:
        await bot.app.shutdown()
        logger.info("Bot shutdown successfully.")
    except Exception as e:
        logger.error(f"Error during bot shutdown: {str(e)}")


# Include API routes
from app.api.endpoints import router  # noqa: E402

app.include_router(router)
