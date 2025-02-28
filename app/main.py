from fastapi import FastAPI

from app.bot.init import TelegramBot
from app.config import Config

import logging
import aiohttp
import sys

# Configure logging
Config.setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TabarSkill Telegram Bot",
    docs_url=None,
    redoc_url=None,
    version="0.1.0"
    )
bot = TelegramBot()


@app.on_event("startup")
async def startup_event():
    try:
        await bot.start()
        logger.info("SYSTEM: Bot started successfully.")
    except aiohttp.ClientError as network_error:
        logger.error(f"SYSTEM: Bot failed to start due to network error")
        raise
    except Exception as e:
        logger.error(f"SYSTEM: Failed to start bot: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    try:
        if bot.app.updater:
            await bot.app.updater.stop()
        await bot.app.stop()
        await bot.app.shutdown()
        logger.info("SYSTEM: Bot hutdown successfully.")
        logger.info("SYSTEM: Bye! > Stop terminal with Ctrl+C")
    except Exception as e:
        logger.error(f"SYSTEM: Error during bot shutdown: {str(e)}")
        try:
            # Force shutdown
            await bot.app.shutdown()
        except Exception:
            pass


# Include API routes
from app.api.endpoints import router

app.include_router(router)
