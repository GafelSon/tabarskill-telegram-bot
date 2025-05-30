# reminder function

# main lib
import asyncio
from datetime import datetime as dt
from datetime import timedelta as tt

# dependencies lib
from sqlalchemy import and_, select
from telegram import (
    Update,
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

# local lib
from app.core.log import start_warning
from app.core.decor import message_object
from app.core.logger import logger
from app.utils.jalali import jcal
from app.database.models import (
    EventModel,
    EventType,
    RepeatType,
    ProfileModel,
    NotificationModel,
)

# logger config
logger = logger(__name__)

(
    EVENT_DATE,
    EVENT_TIME,
    EVENT_TITLE,
    EVENT_IMAGE,
    EVENT_REPEAT,
    EVENT_NOTIFY,
    EVENT_DESCRIPTION,
) = range(7)

QUESTIONS = {
    EVENT_TITLE: "📌 لطفاً عنوان رویداد را وارد کنید:",
    EVENT_DESCRIPTION: "📝 لطفاً توضیحات رویداد را وارد کنید:",
    EVENT_DATE: "📅 لطفاً تاریخ رویداد را انتخاب کنید یا به صورت YYYY/MM/DD وارد کنید:",
    EVENT_TIME: "⏰ لطفاً ساعت رویداد را به صورت HH:MM وارد کنید:",
    EVENT_REPEAT: "🔄 لطفاً نوع تکرار رویداد را انتخاب کنید:",
    EVENT_NOTIFY: "🔔 لطفاً تعداد روزهای قبل از رویداد برای یادآوری را وارد کنید:",
    EVENT_IMAGE: "🖼️ لطفاً تصویر رویداد را ارسال کنید (یا 'بدون تصویر' را بنویسید):",
}

FIELDS = {
    EVENT_TITLE: "title",
    EVENT_DESCRIPTION: "description",
    EVENT_DATE: "date",
    EVENT_TIME: "time",
    EVENT_REPEAT: "repeat",
    EVENT_NOTIFY: "notify_before",
    EVENT_IMAGE: "image",
}

REPEAT_TYPE_MAP = {
    "بدون تکرار": RepeatType.NONE.value,
    "روزانه": RepeatType.DAILY.value,
    "هفتگی": RepeatType.WEEKLY.value,
    "ماهانه": RepeatType.MONTHLY.value,
    "سالانه": RepeatType.YEARLY.value,
}


@message_object
async def handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE, message: Message = None
):
    user = update.effective_user

    if user is None:
        logger.error("SYSTEM:: ReminderHandler:: User not found in here")
        return

    async with context.db.session() as session:
        res = await session.execute(
            select(ProfileModel).where(ProfileModel.telegram_id == str(user.id))
        )
        db_user = res.scalar_one_or_none()

        if not db_user:
            await message.replay_text(start_warning())
            return

    onboarding = (
        f">**📢 پنل اعلانات**\n\n"
        f"سلام 👋\n\n"
        f"به *سیستم مدیریت رویدادها* خوش آمدید\! ✨\n\n"
        f"📌 **امکانات اصلی:**\n"
        f"➖ افزودن *رویداد جدید* به تقویم شخصی\n"
        f"➖ مشاهده 🎓 *رویدادهای دانشگاهی*\n"
        f"➖ تنظیم 🔔 *هشدار یادآوری* برای هر رویداد\n\n"
        f"✅ **مزایا:**\n"
        f"\- دریافت اطلاع‌رسانی خودکار پیش از شروع رویداد\n"
        f"\- مدیریت ساده و سریع برنامه‌های تحصیلی\n\n"
        f"👇 لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"
    )

    # ![TODO] make callback for this keyboard
    keyboard = [
        [
            InlineKeyboardButton("💂‍♂️ شخصی", callback_data="..."),
            InlineKeyboardButton("🎓 دانشگاهی", callback_data="..."),
            InlineKeyboardButton("🛟 راهنما", callback_data="events_help"),
        ],
        [InlineKeyboardButton("🆕 رویداد جدید", callback_data="new_event")],
    ]

    keyboard_layout = InlineKeyboardMarkup(keyboard)

    try:
        await message.reply_photo(
            photo="AgACAgQAAyEGAASLt5ydAANxaDf0-D_ENRnk5lq0GX5d73ygD0AAAi7EMRtRxcBRnp1sajBV8IwBAAMCAAN5AAM2BA",
            caption=onboarding,
            reply_markup=keyboard_layout,
            parse_mode="MarkdownV2",
        )
    except ValueError as e:
        logger.error(f"SYSTEM:: ReminderHandler:: {str(e)}")


async def _back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = None
    await handler(update, context)

    if update.callback_query:
        message = update.callback_query.message
    elif update.message:
        message = update.message

    if message:

        async def delete_after_delay(msg):
            await asyncio.sleep(10)
            await msg.delete()

        asyncio.create_task(delete_after_delay(message))


def new_personal_event():
    pass


def new_university_event():
    pass


def handle_event_input():
    pass


def image_input():
    pass


def cancel_event_creation():
    pass


module = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(new_personal_event, pattern="^new_personal_event$"),
        CallbackQueryHandler(new_university_event, pattern="^new_university_event$"),
    ],
    states={
        EVENT_TITLE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_event_input)
        ],
        EVENT_DESCRIPTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_event_input)
        ],
        EVENT_DATE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_event_input)
        ],
        EVENT_TIME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_event_input)
        ],
        EVENT_REPEAT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_event_input)
        ],
        EVENT_NOTIFY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_event_input)
        ],
        EVENT_IMAGE: [
            MessageHandler(
                (filters.TEXT | filters.PHOTO) & ~filters.COMMAND, image_input
            )
        ],
    },
    fallbacks=[
        MessageHandler(filters.Regex("^🚫 انصراف$"), cancel_event_creation)
    ],  # cancel_conversation
)

__all__ = ["module"]
