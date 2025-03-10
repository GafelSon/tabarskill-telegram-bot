# app.bot.handlers.bio.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy import select

from app.database.models import User
from app.utils.jalali import jcal

import logging

logger = logging.getLogger(__name__)

def escape_markdown(text):
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = str(text).replace(char, f'\{char}')
    return text

async def bio_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user is None:
        logger.error("SYSTEM: No effective user in the update!")
        return

    # Get the user from the database
    async with context.db.session() as session:
        result = await session.execute(select(User).where(User.telegram_id == user.id))
        db_user = result.scalar_one_or_none()
        if not db_user:
            await update.message.reply_text("❌ شما هنوز ثبت‌نام نکرده‌اید. لطفا ابتدا از دستور /start استفاده کنید!")
            return

        bio_text = (
            f">پروفایل دانشجویی\n"
            f"\n\n🔸 *‍نام کاربری*: \@{escape_markdown(db_user.username or 'دانشجوی جدید')}\n\n"
            f"👤 *اطلاعات شخصی:*\n"
            f"    🧩 نام‌ونام‌خانوادگی: {escape_markdown(db_user.first_name or '—')} {escape_markdown(db_user.last_name or '—')}\n"
            f"    📱 شماره تماس: {escape_markdown(db_user.phone or '—')}\n\n"
            f"🎓 *اطلاعات تحصیلی:*\n"
            f"    🔢 شماره دانشجویی: {escape_markdown(db_user.university_id or '—')}\n"
            f"    🏛️ دانشکده: {escape_markdown(db_user.faculty or '—')}\n"
            f"    📚 رشته تحصیلی: {escape_markdown(db_user.major or '—')}\n"
            f"    🗓️ سال ورود: {escape_markdown(db_user.entry_year or '—')}\n\n"
            f"💎 *وضعیت اشتراک:*\n"
            f"    📅 تاریخ ثبت‌نام: {escape_markdown(jcal.format(jcal.tab(db_user.created_at), date_only=True))}\n"
            f"    ⏱️ آخرین فعالیت: {escape_markdown(jcal.format(jcal.tab(db_user.last_interaction)))}\n\n"
            f"**>[چرا برای دستیار دانشگاهی اشتراک ويژه نیاز است؟**](tg://user?id=5455523252)\n\n"
            f"**>[راهنمای استفاده از ربات دستیار**](tg://user?id=5455523252)\n\n"
            f"**>[دسترسی به پشتیبانی فنی ربات دستیار**](tg://user?id=5455523252)\n"
        )

        if db_user.profile:
            # Create inline keyboard with buttons
            keyboard = [
                [InlineKeyboardButton("✏️ ویرایش اطلاعات", callback_data="edit_profile")],
                [InlineKeyboardButton("💎 وضعیت اشتراک", callback_data="show_status")],
                [InlineKeyboardButton("📢 دعوت دوستان", callback_data="invite")],
                [InlineKeyboardButton("❓ پشتیبانی", callback_data="support")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_photo(
                photo=db_user.profile,
                caption=bio_text,
                parse_mode='MarkdownV2',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(bio_text, parse_mode='MarkdownV2')
            
        logger.info(f"Bio requested by user: {user.id}")