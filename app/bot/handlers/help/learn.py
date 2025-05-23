# help handler finction -> learn

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


async def learn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    if not query:
        logger.error("SYSTEM:: HelpHandler:: No callback query found in update")
        return

    onboarding = (
        f">آموزش اولیه ربات\n\n\n"
        f"🎓 *خوش آمدید به ربات دستیار دانشگاهی* 🎓\n\n"
        f"این ربات برای دانشجویان، اساتید و پشتیبانان دانشگاه طراحی شده تا امور آموزشی، اطلاع‌رسانی و مدیریت شخصی دانشگاهی را ساده‌تر کند\\.\n\n"
        f"🤝 *چه کارهایی می‌توانید با ربات انجام دهید؟*\n\n"
        f"📚 *کتابخانه دانشگاهی*: دسترسی به جزوه‌ها، کتاب‌ها، ویدیوهای آموزشی و فایل‌های مهم در دسته‌بندی‌های مختلف\\.\n"
        f"📅 *تقویم دانشگاه*: رویدادها، کلاس‌ها، امتحانات و جلسات را در تقویم شخصی خود ببینید و یادآوری بگیرید\\.\n"
        f"👤 *پروفایل شخصی*: نقش خود را به عنوان دانشجو، استاد یا پشتیبان مدیریت کرده و اطلاعات خود را مشاهده و ویرایش کنید\\.\n"
        f"💳 *اشتراک و توکن*: با فعال‌سازی اشتراک یا خرید توکن به امکانات ویژه مانند دانلود منابع خاص یا شرکت در برنامه‌های ویژه دسترسی داشته باشید\\.\n"
        f"💬 *تعامل با استاد*: ارسال پیام، رزرو جلسه مشاوره، مشاهده بازخورد و امتیازدهی\\.\n"
        f"🏫 *ساختار دانشگاهی*: آشنایی با دانشکده‌ها، گروه‌ها، رشته‌ها و اساتید مرتبط با شما\\.\n\n"
        f"✨ *هدف ما این است که دستیار هوشمند شما در مسیر تحصیلی و دانشگاهی باشید\\.*\n\n"
        f">برای شروع کافی است نقش خود را انتخاب کنید و از امکانات ربات استفاده نمایید\\. اگر نیاز به راهنمایی بیشتر دارید، از طریق منوی پشتیبانی با ما در ارتباط باشید\\.\n"
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
