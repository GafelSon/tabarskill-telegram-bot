# reminder functions -> event input handler

# main lib
# .
# .

# dependencies lib
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

# local lib
from app.core.logger import logger
from app.core.log import internal_error
from app.bot.handlers.reminder.states import EventState, EventInputHandler
from app.bot.handlers.reminder.callbacks.cancel import _cancel
from app.bot.handlers.reminder.get import keyboard
from app.bot.handlers.reminder.callbacks.event_save import save_event

# logger config
logger = logger(__name__)


async def input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        if "user_messages" not in context.user_data:
            context.user_data["user_messages"] = []

        context.user_data["user_messages"].append(update.message)
        current_state = context.user_data.get("current_state", EventState.TITLE)
        text = update.message.text

        if current_state == EventState.PREVIEW and text == "✅ تأیید و ذخیره":
            return await save_event(update, context)

        if "edit_message" in context.user_data:
            await context.user_data["edit_message"].delete()

        next_state, should_continue = await EventInputHandler.handle_input(
            update, context, current_state, text
        )

        if not should_continue:
            return await _cancel(update, context)

        if next_state == EventState.IMAGE:
            context.user_data["edit_message"] = await update.message.reply_text(
                EventInputHandler.QUESTIONS[EventState.IMAGE],
                reply_markup=EventInputHandler.get_keyboard_for_state(EventState.IMAGE),
                parse_mode="MarkdownV2",
            )
            context.user_data["current_state"] = EventState.IMAGE
            return EventState.IMAGE.value

        if next_state == EventState.PREVIEW and current_state != EventState.PREVIEW:
            preview_message = EventInputHandler.generate_preview_message(
                context.user_data
            )
            context.user_data["edit_message"] = await update.message.reply_text(
                preview_message
                + "\n\n"
                + EventInputHandler.QUESTIONS[EventState.PREVIEW],
                reply_markup=EventInputHandler.get_preview_keyboard(),
                parse_mode="MarkdownV2",
            )
            context.user_data["current_state"] = EventState.PREVIEW
            return EventState.PREVIEW.value

        context.user_data["edit_message"] = await update.message.reply_text(
            EventInputHandler.QUESTIONS[next_state],
            reply_markup=EventInputHandler.get_keyboard_for_state(next_state),
            parse_mode="MarkdownV2",
        )
        context.user_data["current_state"] = next_state
        return next_state.value

    except Exception as e:
        logger.error(f"Error in handle_event_input: {str(e)}", exc_info=True)
        await update.message.reply_text(
            internal_error(),
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END
