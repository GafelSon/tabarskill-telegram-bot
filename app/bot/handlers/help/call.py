# help handler finction -> call

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


async def call(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    if not query:
        logger.error("SYSTEM:: HelpHandler:: No callback query found in update")
        return

    onboarding = (
        f">👩‍💼 تماس با پشتیبانی ربات\n\n"
        f"اگر در استفاده از ربات با مشکلی روبرو شدید یا نیاز به راهنمایی بیشتر داشتید، تیم پشتیبانی آماده پاسخگویی به شماست\\.\n\n"
        f"📬 *راه‌های ارتباط با پشتیبانی:*\n"
        f"• ارسال پیام مستقیم به ادمین ربات از طریق دکمه زیر\\.\n"
        f"• استفاده از فرم پشتیبانی موجود در پنل کاربری\\.\n"
        f"• مراجعه به کانال اطلاع‌رسانی جهت مشاهده پاسخ سوالات متداول\\.\n\n"
        f"⏰ *ساعات پاسخگویی:*\n"
        f"همه‌روزه از ساعت ۹ تا ۲۱ \\(به‌جز روزهای تعطیل رسمی\\)\n\n"
        f"ما برای حل سریع و مؤثر مشکلات شما تلاش می‌کنیم و بازخوردهای شما باعث بهبود عملکرد ما خواهد شد\\.\n"
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
