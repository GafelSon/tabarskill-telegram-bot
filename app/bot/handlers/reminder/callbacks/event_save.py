# reminder handler -> event save function

# main lib
from datetime import datetime

# dependencies lib
from sqlalchemy import select
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

# local lib
from app.utils.jalali import jcal
from app.core.logger import logger
from app.core.log import internal_error
from app.database.models import ProfileModel, EventModel, EventType, RepeatType

from ..preview import show_event_preview

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

        event_data = {
            "title": event.title,
            "description": event.description,
            "date": event.date.strftime("%Y-%m-%d"),
            "time": event.date.strftime("%H:%M"),
            "repeat": event.repeat.value
            if hasattr(event.repeat, "value")
            else event.repeat,
            "notify_before": event.notify_before,
            "image": event.image,
        }

        await show_event_preview(
            update, context, event_data=event_data, remove_keyboard=True
        )
        if event_type == EventType.UNIVERSITY.value:
            try:
                async with context.db.session() as session:
                    result = await session.execute(select(ProfileModel))
                    users = result.scalars().all()
                    preview_message = (
                        event_data["title"] + "\n" + event_data["description"]
                    )
                    from app.bot.handlers.reminder.states import EventInputHandler

                    preview_message = EventInputHandler.generate_preview_message(
                        event_data
                    )
                    for user in users:
                        try:
                            if event_data.get("image"):
                                await context.bot.send_photo(
                                    chat_id=user.telegram_id,
                                    photo=event_data["image"],
                                    caption=preview_message,
                                    parse_mode="Markdown",
                                )
                            else:
                                await context.bot.send_message(
                                    chat_id=user.telegram_id,
                                    text=preview_message,
                                    parse_mode="Markdown",
                                )
                        except Exception as e:
                            logger.error(
                                f"Failed to send university event to user {getattr(user, 'telegram_id', None)}: {str(e)}"
                            )
            except Exception as e:
                logger.error(f"Failed to broadcast university event: {str(e)}")

        context.user_data.clear()

        return ConversationHandler.END

    except Exception as e:
        logger.error(f"Error saving event: {str(e)}", exc_info=True)
        await update.message.reply_text(
            internal_error(),
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END
