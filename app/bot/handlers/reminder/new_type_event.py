# reminder function -> new type event

# main lib
# .
# .

# dependencies lib
from sqlalchemy import select
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

# local lib
from app.core.logger import logger
from app.core.log import start_warning, accessibility_error
from app.utils.jalali import jcal
from app.database.models import ProfileModel, EventType, RepeatType

# logger config
logger = logger(__name__)


async def new_personal_event(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    if not query:
        logger.error("SYSTEM:: ReminderHandler:: No callback query found in update")
        return

    async with context.db.session() as session:
        res = await session.execute(
            select(ProfileModel).where(
                ProfileModel.telegram_id == str(query.from_user.id)
            )
        )
        db_user = res.scalar_one_or_none()

        if not db_user:
            await query.answer(start_warning())
            return

        if "user_messages" not in context.user_data:
            context.user_data["user_messages"] = []

        context.user_data["event_type"] = EventType.PERSONAL.value
        context.user_data["edit_message"] = await query.message.reply_text(
            QUESTIONS[EVENT_TITLE], reply_markup=keyboard()
        )
        context.user_data["current_state"] = EVENT_TITLE
        await query.answer()
        return EVENT_TITLE


async def new_university_event(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    if not query:
        logger.error("SYSTEM:: ReminderHandler:: No callback query found in update")
        return

    async with context.db.session() as session:
        res = await session.execute(
            select(ProfileModel).where(
                ProfileModel.telegram_id == str(query.from_user.id)
            )
        )
        db_user = res.scalar_one_or_none()

        if not db_user:
            await query.answer(start_warning())
            return
        if not db_user.flag:
            await query.answer(accessibility_error())
            return

        context.user_data["event_type"] = EventType.UNIVERSITY.value
        if "user_messages" in context.user_data:
            context.user_data["user_messages"] = []

        context.user_data["edit_message"] = await query.message.reply_text(
            QUESTIONS[EVENT_TITLE], reply_markup=keyboard()
        )
        context.user_data["current_state"] = EVENT_TITLE
        context.user_data["confirmed"] = False

        await query.answer()
        return EVENT_TITLE
