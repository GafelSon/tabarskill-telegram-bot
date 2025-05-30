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
    ProfileModel,
    NotificationModel,
)

from .callbacks.cancel import _cancel
from .callbacks.event_type import new_personal_event, new_university_event
from .callbacks.event_new import new_event_callback
from .states import EventState, EventInputHandler
from .callbacks.event_input import input
from .get import (
    EVENT_TITLE,
    EVENT_DESCRIPTION,
    EVENT_DATE,
    EVENT_TIME,
    EVENT_REPEAT,
    EVENT_IMAGE,
    REPEAT_TYPE_MAP,
)

# logger config
logger = logger(__name__)


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
            InlineKeyboardButton("💂‍♂️ شخصی", callback_data="new_personal_event"),
            InlineKeyboardButton("🎓 دانشگاهی", callback_data="new_university_event"),
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


async def image_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    text = message.text if message.text else ""

    if text == "بدون تصویر":
        context.user_data["image"] = None
        return EventState.PREVIEW.value

    if message.photo:
        photo = message.photo[-1]
        context.user_data["image"] = photo.file_id
        return EventState.PREVIEW.value

    await message.reply_text(
        "❌ لطفاً یک تصویر ارسال کنید یا 'بدون تصویر' را بنویسید.",
        reply_markup=EventInputHandler.get_keyboard_for_state(EventState.IMAGE),
    )
    return EventState.IMAGE.value


module = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(new_event_callback, pattern="^new_event$"),
        CallbackQueryHandler(new_personal_event, pattern="^new_personal_event$"),
        CallbackQueryHandler(new_university_event, pattern="^new_university_event$"),
    ],
    states={
        EventState.TITLE.value: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, input)
        ],
        EventState.DESCRIPTION.value: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, input)
        ],
        EventState.DATE.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, input)],
        EventState.TIME.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, input)],
        EventState.REPEAT.value: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, input)
        ],
        EventState.NOTIFY.value: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, input)
        ],
        EventState.IMAGE.value: [
            MessageHandler(
                (filters.TEXT | filters.PHOTO) & ~filters.COMMAND, image_input
            )
        ],
        EventState.PREVIEW.value: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, input)
        ],
    },
    fallbacks=[MessageHandler(filters.Regex("^🚫 انصراف$"), _cancel)],
)

__all__ = ["module", "_back"]
