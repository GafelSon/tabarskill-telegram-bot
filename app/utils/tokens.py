# app.utils.tokens.py
import logging

from sqlalchemy import select
from telegram import Update
from telegram.ext import ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from app.database.models import User

logger = logging.getLogger(__name__)

# Define the check_tokens function
def check_tokens(cost: float = 0.75):
    def decorator(func):
        async def wrapper(
            update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
        ):
            user = update.effective_user
            if user is None:
                logger.error("SYSTEM: No effective user in the update")
                return
            
            # Get the user from the database
            async with context.db.session() as session:
                result = await session.execute(
                    select(User).where(User.telegram_id == user.id)
                )
                db_user = result.scalar_one_or_none()

                if not db_user:
                    await update.message.reply_text("❌ شما هنوز ثبت‌نام نکرده‌اید. لطفا ابتدا از دستور /start استفاده کنید!")
                    return

                if db_user.tokens < cost:
                    keyboard = [[InlineKeyboardButton("💎 خرید اشتراک ویژه", callback_data="premium")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(
                        f">موجودی ناکافی\!\n\n\n"
                        f"🔔 دانجشوی عزیز، برای استفاده از این امکان، اعتبار کافی ندارید\.\n\n"

                        f"💰 *اعتبار مورد نیاز:* {str(cost)} *توکن*\n"
                        f"👛 *موجودی شما:* {str(db_user.tokens)} *توکن*\n\n"
                        f"> ✨ برای افزایش اعتبار و استفاده از امکانات ویژه، روی دکمه زیر کلیک کنید:",
                        parse_mode="MarkdownV2",
                        reply_markup=reply_markup
                    )
                    return

                db_user.tokens -= cost
                await session.commit()
                return await func(update, context, *args, **kwargs)

        return wrapper

    return decorator
