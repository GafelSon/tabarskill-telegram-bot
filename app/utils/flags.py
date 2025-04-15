import logging
from collections import defaultdict
from datetime import datetime, timedelta
from functools import wraps

from sqlalchemy import select
from telegram import Update
from telegram.ext import ContextTypes

from app.database.models.profile import ProfileModel

# Track failed attempts by user
_failed_attempts = defaultdict(int)
_last_attempt_time = defaultdict(datetime.now)


def require_flag(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)

        # Reset counter if last attempt was more than 1 hour ago
        if datetime.now() - _last_attempt_time[user_id] > timedelta(hours=1):
            _failed_attempts[user_id] = 0

        _last_attempt_time[user_id] = datetime.now()

        async with context.bot_data["db"].session() as session:
            result = await session.execute(
                select(ProfileModel).where(ProfileModel.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user or not user.flag:
                _failed_attempts[user_id] += 1
                if _failed_attempts[user_id] >= 50:
                    await update.message.reply_text(
                        "⚠️ این قابلیت فقط برای کاربران دارای پرچم در دسترس است. "
                        "لطفاً برای اطلاعات بیشتر با پشتیبانی تماس بگیرید. 🔒"
                    )
                return

            _failed_attempts[user_id] = 0
            return await func(update, context)

    return wrapper


async def has_flag(telegram_id, db=None) -> bool:
    """Check if a user has the flag feature enabled."""
    if db is None:
        return False

    try:
        async with db.session() as session:
            result = await session.execute(
                select(ProfileModel).where(
                    ProfileModel.telegram_id == str(telegram_id)
                )
            )
            user = result.scalar_one_or_none()
            if user is None:
                return False
            return bool(user.flag)
    except Exception as e:
        logging.error(f"Error checking flag for user {telegram_id}: {str(e)}")
        return False
