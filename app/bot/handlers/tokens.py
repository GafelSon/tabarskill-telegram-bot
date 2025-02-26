# app.bot.handlers.tokens.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy import select

from app.database.models import User

import logging

logger = logging.getLogger(__name__)

def escape_markdown(text):
    """Escape special characters for MarkdownV2 format."""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = str(text).replace(char, f'\{char}')
    return text

async def tokens_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user is None:
        logger.error("System: No effective user in the update")
        return
    
    # Get the user from the database
    async with context.db.session() as session:
        result = await session.execute(select(User).where(User.telegram_id == user.id))
        db_user = result.scalar_one_or_none()

        if not db_user:
            await update.message.reply_text("❌ شما هنوز ثبت‌نام نکرده‌اید. لطفا ابتدا از دستور /start استفاده کنید!")
            return

        tokens_message = (
            f">اعتبار دانشجویی\n\n\n"
            f"💫 *وضعیت اشتراک شما*:\n\n"
            f"*نام کاربری:* \@{escape_markdown(db_user.username or 'دانشجوی جدید')}\n\n"
            f"💎 *نوع اشتراک:* {'✨ ویژه' if db_user.is_premium else '🔹 رایگان'}\n"
            f"🎫 *توکن‌های باقیمانده:* {db_user.tokens or 0}\n"
            f"📅 *تاریخ عضویت:* {db_user.created_at.strftime('%y/%m/%d %H:%M')}\n\n"
            f">{'✨ شما دسترسی ویژه دارید و می‌توانید از تمام امکانات ربات استفاده کنید\.' if db_user.is_premium else '⭐️ برای استفاده از امکانات ویژه، اشتراک تهیه کنید\.'}"
        )

        # Create inline keyboard with buttons /todo: add callback data
        keyboard = [
            [InlineKeyboardButton("🕹️ آموزش ربات دستیار", callback_data="test")],
            [InlineKeyboardButton("💎 خرید اشتراک ویژه", callback_data="test")],
            [InlineKeyboardButton("💸 کسب درآمد از طریق ربات", callback_data="test")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_photo(
            photo="AgACAgQAAxkDAAIDS2e5-xgWr1Q44y1XD4sptI38U-eQAALLxzEbwyPQUQZkjCRRddscAQADAgADdwADNgQ",
            caption=tokens_message,
            reply_markup=reply_markup,
            parse_mode='MarkdownV2'
        )