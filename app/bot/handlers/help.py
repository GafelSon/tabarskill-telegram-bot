# app.bot.handlers.help.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_message = (
        f">دستورالعمل\n\n\n"
        f"✨ *دستورالعمل استفاده از ربات* ✨\n\n"
        f"به پنل راهنمای ربات دستیار دانشگاهی دانشگاه ملی مهارت مازندران خوش آمدید\. در اینجا می‌توانید به راحتی به امکانات دانشگاه و خدمات مختلف دسترسی داشته باشید\.\n\n"
        f"*🌟 امیدواریم بتوانید بیشترین استفاده را از این ربات داشته باشید و در امور دانشگاهی به شما کمک کند\!*\n\n"
        f">اگر سوالی داشتید یا نیاز به کمک بیشتری داشتید، می‌توانید به راحتی از طریق ادمین راهنمایی بگیرید\."
    )

    # Create inline keyboard with buttons /todo: add callback data
    keyboard = [
        [InlineKeyboardButton("🕹️ آموزش ربات دستیار", callback_data="test")],
        [InlineKeyboardButton("💻 چرا این ربات فعالیت میکند؟", callback_data="test")],
        [InlineKeyboardButton("👩‍💼 تماس با پشتیبانی ربات", callback_data="test")],
        [InlineKeyboardButton("👨‍💻 تماس با پشتیبانی فنی", callback_data="test")],
        [InlineKeyboardButton("📝 فرم ارسال نظرات و پیشنهادات", callback_data="test")], 
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_photo(
        photo="AgACAgQAAxkDAAIDS2e5-xgWr1Q44y1XD4sptI38U-eQAALLxzEbwyPQUQZkjCRRddscAQADAgADdwADNgQ",
        caption=help_message,
        reply_markup=reply_markup,
        parse_mode="MarkdownV2",
    )