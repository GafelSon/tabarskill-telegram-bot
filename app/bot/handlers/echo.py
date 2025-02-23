from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

async def echo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo the user message."""
    if update.message and update.message.text:
        logger.info(f"Received message from {update.effective_user.id}: {update.message.text}")
        await update.message.reply_text(update.message.text)
    else:
        logger.warning(f"Received update without message text: {update}")