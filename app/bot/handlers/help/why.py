# help handler finction -> why

# main lib
# .
# .

# dependencies lib
from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

# local lib
from app.core.logger import logger
from app.bot.handlers.help import gotit

# conig logger
logger = logger(__name__)


async def why(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    if not query:
        logger.error("SYSTEM:: HelpHandler:: No callback query found in update")
        return

    onboarding = (
        f">💻 چرا این ربات فعالیت می‌کند؟\n\n"
        f"این ربات با هدف ساده‌سازی و هوشمندسازی فرایندهای دانشگاهی طراحی شده است\\.\n"
        f"در بسیاری از مواقع، دسترسی به اطلاعات، فایل‌ها، برنامه‌ها و ارتباط با اعضای دانشگاه زمان‌بر و پراکنده است\\.\n"
        f"ما تلاش کرده‌ایم این چالش‌ها را با یک دستیار مرکزی حل کنیم\\.\n\n"
        f"🎯 *اهداف اصلی ربات:*\n"
        f"• ایجاد دسترسی سریع و یکپارچه به منابع آموزشی و اداری\\.\n"
        f"• کاهش سردرگمی دانشجویان در امور دانشگاهی\\.\n"
        f"• ارتقاء تعامل بین دانشجو، استاد و پشتیبان\\.\n"
        f"• افزایش نظم با استفاده از تقویم، یادآورها و اطلاع‌رسانی لحظه‌ای\\.\n\n"
        f"🌐 این ربات بخشی از پروژه هوشمندسازی دانشگاه ملی مهارت مازندران است و به مرور، امکانات جدیدی نیز به آن اضافه خواهد شد\\.\n"
    )

    buttons = [[InlineKeyboardButton("☑️ متوجه شدم...", callback_data="gotit")]]

    onboard = await query.message.reply_text(
        text=onboarding,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="MarkdownV2",
    )

    # Schedule deletion
    context.job_queue.run_once(
        gotit,
        when=1800,
        data={
            "chat_id": onboard.chat_id,
            "message_id": onboard.message_id,
        },
    )
