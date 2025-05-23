# help handler function

# main lib

# dependencies lib
from telegram.ext import ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Message

# local lib
from app.utils.flags import has_flag
from app.core.decor import message_object


@message_object
async def handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE, message: Message = None
) -> None:
    query = update.callback_query

    onboarding = (
        ">دستورالعمل\n\n\n"
        "✨ *دستورالعمل استفاده از ربات* ✨\n\n"
        "به پنل راهنمای ربات دستیار دانشگاهی دانشگاه ملی مهارت مازندران خوش آمدید\. در اینجا می‌توانید به راحتی به امکانات دانشگاه و خدمات مختلف دسترسی داشته باشید\.\n\n"
        "*🌟 امیدواریم بتوانید بیشترین استفاده را از این ربات داشته باشید و در امور دانشگاهی به شما کمک کند\!*\n\n"
        ">اگر سوالی داشتید یا نیاز به کمک بیشتری داشتید، می‌توانید به راحتی از طریق ادمین راهنمایی بگیرید\."
    )

    keyboard = [
        [InlineKeyboardButton("🕹️ آموزش ربات دستیار", callback_data="learn")],
        [InlineKeyboardButton("💻 چرا این ربات فعالیت میکند؟", callback_data="why")],
        [InlineKeyboardButton("👩‍💼 تماس با پشتیبانی ربات", callback_data="call")],
        [InlineKeyboardButton("👨‍💻 تماس با پشتیبانی فنی", callback_data="support")],
        [
            InlineKeyboardButton(
                "📝 فرم ارسال نظرات و پیشنهادات", callback_data="feedback"
            )
        ],
    ]
    keyboard_layout = InlineKeyboardMarkup(keyboard)

    await message.reply_photo(
        photo="AgACAgQAAyEGAASLt5ydAAMmZ_yo0BP-GMN8Vjv7pn9FojWPr4IAAnDGMRstPuFT2ygGVy3kLJ8BAAMCAANtAAM2BA",
        caption=onboarding,
        reply_markup=keyboard_layout,
        parse_mode="MarkdownV2",
    )


async def gotit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    if not query:
        logger.error("SYSTEM:: GotItHandler:: No callback query found in update")
        return

    await query.message.delete()
    await query.answer()
