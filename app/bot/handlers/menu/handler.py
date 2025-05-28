# menu handler function

# main lib

# dependencies lib
from telegram.ext import ContextTypes
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update

# local lib
from app.core.logger import logger
from app.utils.flags import has_flag

# logger config
logger = logger(__name__)


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id

    keyboard = [
        [KeyboardButton("🏠 تالار اصلی"), KeyboardButton("👤 پروفایل من")],
        [KeyboardButton("🎒 کیف پول"), KeyboardButton("📚 منابع درسی")],
        [KeyboardButton("⏰ نمایه امروز"), KeyboardButton("📆 تقویم ماهانه")],
        [KeyboardButton("🎃 رویدادها"), KeyboardButton("🔍 راهنمای استفاده")],
    ]

    if await has_flag(user, context.bot_data["db"]):
        logger.info(f"User {user} accessed menu with flag privileges.")
        keyboard.append([KeyboardButton("💰 کیف پول"), KeyboardButton("📤 آپلود")])

    keyboard_layout = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    onboarding = (
        f">*منوی اصلی*\n\n\n"
        f"به تالار مهارت خوش آمدید\!\n"
        f"از منوی زیر می‌توانید به بخش‌های مختلف دسترسی پیدا کنید\.\n"
        f"لطفاً یکی از گزینه‌ها را انتخاب نمایید:"
    )

    await update.message.reply_text(
        text=onboarding, reply_markup=keyboard_layout, parse_mode="MarkdownV2"
    )
