# help handler finction -> support

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


async def support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    if not query:
        logger.error("SYSTEM:: HelpHandler:: No callback query found in update")
        return

    onboarding = (
        f">👨‍💻 تماس با پشتیبانی فنی\n\n"
        f"در صورتی که با خطاهای فنی در عملکرد ربات، اپلیکیشن یا سامانه‌های دانشگاه روبرو شدید، می‌توانید از طریق راه‌های زیر با تیم فنی تماس بگیرید\\:\n\n"
        f"🔧 *راه‌های ارتباط با پشتیبانی فنی:*\n"
        f"• گزارش خطا از طریق دکمه 'گزارش مشکل' در منو ربات\\.\n"
        f"• ارسال کد خطا یا تصویر مشکل به آدرس پشتیبانی فنی\\.\n"
        f"• استفاده از فرم ثبت خطا در پنل کاربری برای پیگیری سریع‌تر\\.\n\n"
        f"💡 *نکات مهم:*\n"
        f"لطفاً در هنگام ارسال گزارش، نوع خطا، زمان وقوع، و توضیح دقیق مشکل را ذکر کنید تا تیم فنی بتواند سریع‌تر آن را بررسی و رفع کند\\.\n\n"
        f"⏰ *ساعات پشتیبانی فنی:*\n"
        f"از ۹ صبح تا ۶ عصر، روزهای کاری هفته\\.\n\n"
        f"با همراهی شما، کیفیت خدمات فنی ربات همواره در حال بهبود است\\.\n"
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
