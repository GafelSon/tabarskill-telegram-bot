from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.utils.flags import has_flag


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        # Basic commands for all users
        [InlineKeyboardButton("🔍 راهنما", callback_data="help")],
        [InlineKeyboardButton("⏰ زمان", callback_data="time")],
        [InlineKeyboardButton("📝 بیوگرافی", callback_data="bio")],
        [InlineKeyboardButton("📅 تقویم", callback_data="calendar")],
    ]

    print(
        f"User {update.effective_user.id} flag check: {await has_flag(update.effective_user.id, context.bot_data['db'])}"
    )

    print(update.effective_user.id)
    if await has_flag(update.effective_user.id, context.bot_data['db']):
        keyboard.append(
            [
                InlineKeyboardButton("💰 کیف پول", callback_data="wallet"),
                InlineKeyboardButton("📤 آپلود", callback_data="upload"),
            ]
        )

    reply_markup = InlineKeyboardMarkup(keyboard)
    message = (
        "🎯 *منوی اصلی*\n\n"
        "به منوی اصلی خوش آمدید\. لطفاً یکی از گزینه‌های زیر را انتخاب کنید:\."
    )

    await update.message.reply_text(
        text=message, reply_markup=reply_markup, parse_mode="MarkdownV2"
    )
