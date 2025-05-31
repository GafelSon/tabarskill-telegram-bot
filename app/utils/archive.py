# Utils -> archive module

# main lib
import os
from typing import Optional

# dependencies lib
from telegram import Bot

# local lib
from app.core.logger import logger

# logger config
logger = logger(__name__)


# preInctance
ARCHIVE_CHANNEL = os.getenv("ARCHIVE_CHANNEL", "")


async def get_archive_channel(bot: Bot) -> Optional[str]:
    try:
        chat = await bot.get_chat(ARCHIVE_CHANNEL)
        logger.info(f"Found archive channel: {chat.id}")
        return chat.id
    except Exception as e:
        logger.error(f"Error getting archive channel: {str(e)}")
        return None


async def verify_archive_channel(bot: Bot) -> bool:
    try:
        bot_member = await bot.get_chat_member(chat_id=ARCHIVE_CHANNEL, user_id=bot.id)
        is_admin = bot_member.status in ["administrator", "creator"]
        logger.info(f"Bot's status in archive channel: {bot_member.status}")
        return is_admin
    except Exception as e:
        logger.error(f"Error verifying archive channel access: {str(e)}")
        return False
