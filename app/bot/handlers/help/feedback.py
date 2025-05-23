# help handler finction -> feedback

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


async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    if not query:
        logger.error("SYSTEM:: HelpHandler:: No callback query found in update")
        return

    onboarding = (
        f">👨‍💻 تماس با پشتیبانی فنی\n\n"
        f"در صورتی که با مشکلات فنی روبرو شدید، مانند خطا در عملکرد ربات یا دسترسی نداشتن به بخش‌های مختلف، می‌توانید از راه‌های زیر با تیم فنی در ارتباط باشید\\:\n\n"
        f"• ارسال پیام به اکانت پشتیبانی فنی ربات\\.\n"
        f"• استفاده از گزینه 'گزارش مشکل' در منو اصلی برای ثبت مستقیم خطاها\\.\n"
        f"• ارسال اسکرین‌شات یا توضیح دقیق مشکل برای بررسی سریع‌تر\\.\n\n"
        f"لطفاً در گزارش خود زمان، نوع خطا، و توضیح واضحی از مشکل ارائه دهید تا فرآیند رفع خطا سریع‌تر انجام شود\\.\n\n"
        f"⏱️ پشتیبانی فنی در روزهای کاری از ساعت ۹ تا ۱۸ پاسخگوی شما خواهد بود\\.\n"
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
