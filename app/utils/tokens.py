from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy import select
from app.database.models import User
import logging

logger = logging.getLogger(__name__)

def check_tokens(cost: float = 0.75):
    def decorator(func):
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user = update.effective_user
            if user is None:
                logger.error("No effective user in the update")
                return

            async with context.db.session() as session:
                result = await session.execute(
                    select(User).where(User.telegram_id == user.id)
                )
                db_user = result.scalar_one_or_none()

                if not db_user:
                    await update.message.reply_text("Please use /start first!")
                    return

                if db_user.tokens < cost:
                    await update.message.reply_text(
                        f"⚠️ *موجودی ناکافی!*\n\n"
                        f"💰 *اعتبار مورد نیاز:* {str(cost)} *توکن*\n"
                        f"👛 *موجودی شما:* {str(db_user.tokens)} *توکن*\n\n"
                        f"✨ برای افزایش اعتبار و استفاده از امکانات ویژه:\n"
                        f"🎁 دستور /premium را ارسال کنید",
                        parse_mode='Markdown'
                    )
                    return

                db_user.tokens -= cost
                await session.commit()
                return await func(update, context, *args, **kwargs)

        return wrapper
    return decorator
