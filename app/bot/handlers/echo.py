# app.bot.handlers.echo.py
# THIS IS TEST HANDLER FOR TESTING PURPOSES
from telegram.ext import ContextTypes
from telegram import Update

import logging

logger = logging.getLogger(__name__)

async def echo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo the user message."""
    if update.message and update.message.text:
        await update.message.reply_text(
            text=f"🤖 ربات: گفتی {update.message.text}؟ منم گفتم! حالا دو برابر مهم شد! 📢📢😆"
        )
    else:
        logger.warning(f"SYSTEM: Received update without message text: {update}")