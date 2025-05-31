# reminder function -> cancel event callback


# main lib
import datetime as dt
from typing import Dict, List, Optional, Union, Any

# dependencies lib
from telegram import (
    Update,
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ConversationHandler,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

# local lib
from app.core.log import cancel_alert
from app.core.logger import logger


async def _cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if "user_messages" in context.user_data:
        for message in context.user_data["user_messages"]:
            try:
                await message.delete()
            except Exception as e:
                pass
        del context.user_data["user_messages"]

    await update.message.reply_text(
        cancel_alert("اضافه کردن رویداد"),
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END
