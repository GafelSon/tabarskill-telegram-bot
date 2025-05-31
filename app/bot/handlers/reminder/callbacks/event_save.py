# reminder handler -> event save function

# main lib
from datetime import datetime

# dependencies lib
from telegram.ext import ContextTypes, ConversationHandler

# local lib
from app.core.logger import logger
from app.core.log import internal_error
from app.utils.jalali import jcal
from app.database.models import EventModel, EventType, RepeatType

# logger config
logger = logger(__name__)


async def save_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        title = context.user_data.get("title")
        description = context.user_data.get("description")
        date_str = context.user_data.get("date")
        time_str = context.user_data.get("time")
        event_type = context.user_data.get("event_type")
        repeat_type = context.user_data.get("repeat", RepeatType.NONE.value)
        notify_before = context.user_data.get("notify_before")
        image = context.user_data.get("image")
        date_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

        event = EventModel(
            title=title,
            description=description,
            date=date_time,
            type=EventType(event_type),
            repeat=RepeatType(repeat_type),
            created_by=str(update.effective_user.id),
            notify_before=notify_before,
            image=image,
            confirmed=event_type != EventType.UNIVERSITY.value,
        )

        async with context.db.session() as session:
            session.add(event)
            await session.commit()

        await update.message.reply_text(
            "✅ رویداد با موفقیت ثبت شد!", reply_markup=ReplyKeyboardRemove()
        )
        context.user_data.clear()

        return ConversationHandler.END

    except Exception as e:
        logger.error(f"Error saving event: {str(e)}", exc_info=True)
        await update.message.reply_text(
            internal_error(),
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END
