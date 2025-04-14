# app.bot.handlers.time.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.utils.jalali import calendar, jcal


def escape_markdown(text):
    special_chars = [
        "_",
        "*",
        "[",
        "]",
        "(",
        ")",
        "~",
        "`",
        ">",
        "#",
        "+",
        "-",
        "=",
        "|",
        "{",
        "}",
        ".",
        "!",
    ]
    for char in special_chars:
        text = text.replace(char, f"\{char}")
    return text


async def time_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    current_jalali = jcal._get_time()
    weekday = calendar.WEEKDAYS[current_jalali.weekday()]
    gregorian_date = current_jalali.togregorian()
    gregorian_month = calendar.GREGORIAN_MONTHS[gregorian_date.month]
    header, calendar_markup = calendar.get_month_calendar()

    try:
        events = await calendar.get_events_for_date(current_jalali)
        events_text = (
            "\n\n".join(events)
            if events
            else "  \|\_ 📭 رویدادی برای امروز ثبت نشده"
        )
    except Exception:
        events_text = "  \|\_ ⚠️ خطا در دریافت رویدادها"

    time_message = (
        f">تقویم دانشجویی\n\n\n"
        f"👋 *دانشجوی عزیز وقت بخیر*\n\n"
        f"💫 امروز {weekday}\n"
        f"☀️ {current_jalali.day} {calendar.MONTH_NAMES[current_jalali.month - 1]} ماه {current_jalali.year} هجری شمسی\n"
        f"🌲 {gregorian_date.day} {gregorian_month} {gregorian_date.year} میلادی\n\n"
        f"🗓️ *لیست رویدادهای امروز:*\n"
        f"{events_text}\n\n"
        f">روش سپری کردن زمان است که شخصیت ما را تعریف می‌کند – جاناتان استرین"
    )

    # Create the keyboard with the calendar
    keyboard = [
        [
            InlineKeyboardButton("⚙️ مدیریت", callback_data="settings_calendar"),
            InlineKeyboardButton("🗓️ تقویم", callback_data="show_calendar"),
        ]
    ]

    await update.message.reply_photo(
        photo=calendar.get_season_image(),
        caption=time_message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="MarkdownV2",
    )
