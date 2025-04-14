# app.bot.handlers.echo.py
# THIS IS TEST HANDLER FOR TESTING PURPOSES
import logging

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


def escape_markdown(text):
    special_chars = [
        "_",
        "*",
        "[",
        "]",
        "(",
        ")",
        "~",
        "`",
        ">",
        "#",
        "+",
        "-",
        "=",
        "|",
        "{",
        "}",
        ".",
        "!",
    ]
    escaped_text = str(text)
    for char in special_chars:
        escaped_text = escaped_text.replace(char, f"\\{char}")
    return escaped_text


async def echo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo the user message."""
    if update.message and update.message.text:
        message_text = escape_markdown(update.message.text)
        response_text = escape_markdown(
            f"🤖 ربات: گفتی {message_text}؟ منم گفتم! حالا دو برابر مهم شد! 📢📢😆"
        )
        await update.message.reply_text(text=response_text, parse_mode="MarkdownV2")
    else:
        logger.warning(
            f"SYSTEM: Received update without message text: {update}"
        )
