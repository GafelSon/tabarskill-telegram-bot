# Utils -> show module

# main lib
import importlib
import os

# dependencies lib
from telegram import Update
from telegram.ext import CallbackContext

# lcoal lib
from app.core.decor import message_object


def get_handlers():
    handlers = {}
    handlers_path = os.path.join(os.path.dirname(__file__), "..", "bot", "handlers")

    if not os.path.exists(handlers_path):
        return handlers

    for item in os.listdir(handlers_path):
        item_path = os.path.join(handlers_path, item)

        if (
            os.path.isdir(item_path)
            and not item.startswith(".")
            and item != "__pycache__"
        ):
            handler_file = os.path.join(item_path, "handler.py")
            if os.path.exists(handler_file):
                handlers[item] = f"app.bot.handlers.{item}.handler"
            else:
                handlers[item] = f"app.bot.handlers.{item}"

    return handlers


SHOW_HANDLERS = get_handlers()


async def handle_show_query(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if not query or not query.data.startswith("show_"):
        return
    command_name = query.data[5:]

    if command_name not in SHOW_HANDLERS:
        await query.answer(f"Command '{command_name}' not found!")
        return
    try:
        module_path = SHOW_HANDLERS[command_name]
        module = importlib.import_module(module_path)
        handler = getattr(module, "handler", None)

        if handler and callable(handler):
            await query.answer()
            await handler(update, context)
        else:
            await query.answer(f"Command function not found!")
    except Exception as e:
        await query.answer("An error occurred while processing your request!")
