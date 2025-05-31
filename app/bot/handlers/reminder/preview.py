# reminder handler -> preview handler

# main lib
# .
# .

# dependencies lib
# .
# .

# local lib
from .states import EventInputHandler, EventState


from telegram import ReplyKeyboardRemove

async def show_event_preview(update, context, event_data=None, remove_keyboard=False):
    user_data = event_data if event_data is not None else context.user_data
    preview_message = EventInputHandler.generate_preview_message(user_data)
    if remove_keyboard:
        keyboard = ReplyKeyboardRemove()
    else:
        keyboard = EventInputHandler.get_preview_keyboard()

    if user_data.get("image"):
        await update.message.reply_photo(
            photo=user_data["image"], caption=preview_message, reply_markup=keyboard
        )
    else:
        await update.message.reply_text(preview_message, reply_markup=keyboard)
