# Utils -> Flags

# main lib
from functools import wraps
from collections import defaultdict
from datetime import datetime as dt
from datetime import timedelta as tt

# dependencies lib
from sqlalchemy import select
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

# local lib
from app.core.logger import logger
from app.database.models.profile import ProfileModel

# Track failed attempts by user
_failed_attempts = defaultdict(int)
_last_attempt_time = defaultdict(dt.now)


def require_flag(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)

        if dt.now() - _last_attempt_time[user_id] > tt(hours=1):
            _failed_attempts[user_id] = 0
        _last_attempt_time[user_id] = dt.now()

        async with context.bot_data["db"].session() as session:
            result = await session.execute(
                select(ProfileModel).where(ProfileModel.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user or not user.flag:
                _failed_attempts[user_id] += 1
                if _failed_attempts[user_id] >= 50:
                    await update.message.reply_text(...)
                return ConversationHandler.END
            _failed_attempts[user_id] = 0

            if isinstance(func, ConversationHandler):
                return func
            return await func(update, context)

    return wrapper


async def has_flag(telegram_id, db=None) -> bool:
    if db is None:
        return False
    try:
        async with db.session() as session:
            result = await session.execute(
                select(ProfileModel).where(ProfileModel.telegram_id == str(telegram_id))
            )
            user = result.scalar_one_or_none()
            if user is None:
                return False
            return bool(user.flag)
    except Exception as e:
        logging.error(f"Error checking flag for user {telegram_id}: {str(e)}")
        return False
