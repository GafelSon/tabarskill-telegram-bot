from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning
)

"""
+------+.      +------+       +------+       +------+      .+------+
|`.    | `.    |\     |\      |      |      /|     /|    .' |    .'|
|  `+--+---+   | +----+-+     +------+     +-+----+ |   +---+--+'  |
|   |  |   |   | |    | |     |      |     | |    | |   |   |  |   |
+---+--+.  |   +-+----+ |     +------+     | +----+-+   |  .+--+---+
 `. |    `.|    \|     \|     |      |     |/     |/    |.'    | .'
   `+------+     +------+     +------+     +------+     +------+'
"""

# library
import logging
import aiohttp
from fastapi import FastAPI

from app.config import Config
from app.core.logger import setup
from app.bot.init import TelegramBot

# logger setup
setup()  # from logger

logger = logging.getLogger(__name__)

app = FastAPI(
    title="TabarSkill Telegram Bot",
    docs_url=None,
    redoc_url=None,
    version="0.1.0",
)
bot = TelegramBot()


@app.on_event("startup")
async def startup_event():
    try:
        await bot.start()
        logger.info("SYSTEM:: Bot started successfully.")
    except aiohttp.ClientError:
        logger.error("SYSTEM: Bot failed to start due to network error")
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
        logger.info("SYSTEM:: Bot hutdown successfully.")
        logger.info("SYSTEM:: Stop terminal with Ctrl+C")
    except Exception as e:
        logger.error(f"SYSTEM:: Error during bot shutdown: {str(e)}")
        try:
            # Force shutdown
            await bot.app.shutdown()
        except Exception:
            pass


# Include API routes
from app.api.endpoints import router

app.include_router(router)
