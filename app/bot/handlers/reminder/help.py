# reminder function -> help

# main lib

# dependencies lib
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes

# local lib
from app.core.logger import logger

# logger config
logger = logger(__name__)


async def events_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        logger.error(
            "SYSTEM:: ReminderHandler:: Help:: No callback query found in update"
        )
        return

    onboarding = (
        f"🧠 راهنمای استفاده از یادآور\n\n"
        f"🔹 1️⃣ رویدادهای شخصی:\n"
        f" 🔸 مخصوص کارهای شخصی شما\n"
        f" 🔒 فقط خودتان می‌توانید ببینید\n"
        f" ⏰ امکان تنظیم یادآور\n\n"
        f"🔹 2️⃣ رویدادهای دانشگاهی:\n"
        f" 🏫 مخصوص فعالیت‌های دانشگاهی\n"
        f" 👥 قابل مشاهده برای همه کاربران\n"
        f" 🏅 ایجاد رویداد فقط برای کاربران ویژه\n\n"
        f"🔹 3️⃣ تنظیمات:\n"
        f" 🛠 مدیریت تمام یادآورها\n"
        f" 🔔 تنظیم و کنترل اعلان‌ها\n"
    )

    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back2reminder")]]
    keyboard_layout = InlineKeyboardMarkup(keyboard)

    await query.answer()
    await query.edit_message_caption(
        caption=onboarding,
        reply_markup=keyboard_layout,
        parse_mode="Markdown",
    )
