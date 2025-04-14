# app.bot.handlers.help.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


async def help_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    help_message = (
        ">دستورالعمل\n\n\n"
        "✨ *دستورالعمل استفاده از ربات* ✨\n\n"
        "به پنل راهنمای ربات دستیار دانشگاهی دانشگاه ملی مهارت مازندران خوش آمدید\. در اینجا می‌توانید به راحتی به امکانات دانشگاه و خدمات مختلف دسترسی داشته باشید\.\n\n"
        "*🌟 امیدواریم بتوانید بیشترین استفاده را از این ربات داشته باشید و در امور دانشگاهی به شما کمک کند\!*\n\n"
        ">اگر سوالی داشتید یا نیاز به کمک بیشتری داشتید، می‌توانید به راحتی از طریق ادمین راهنمایی بگیرید\."
    )

    # Create inline keyboard with buttons /todo: add callback data
    keyboard = [
        [InlineKeyboardButton("🕹️ آموزش ربات دستیار", callback_data="test")],
        [
            InlineKeyboardButton(
                "💻 چرا این ربات فعالیت میکند؟", callback_data="test"
            )
        ],
        [
            InlineKeyboardButton(
                "👩‍💼 تماس با پشتیبانی ربات", callback_data="test"
            )
        ],
        [
            InlineKeyboardButton(
                "👨‍💻 تماس با پشتیبانی فنی", callback_data="test"
            )
        ],
        [
            InlineKeyboardButton(
                "📝 فرم ارسال نظرات و پیشنهادات", callback_data="test"
            )
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_photo(
        photo="AgACAgQAAyEGAASLt5ydAAMmZ_yo0BP-GMN8Vjv7pn9FojWPr4IAAnDGMRstPuFT2ygGVy3kLJ8BAAMCAANtAAM2BA",
        caption=help_message,
        reply_markup=reply_markup,
        parse_mode="MarkdownV2",
    )
