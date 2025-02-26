# app.bot.handlers.__init__.py
from telegram.ext import CommandHandler, MessageHandler, filters
from telegram.ext import CallbackQueryHandler
from functools import wraps

from .start import start_handler
from .help import help_handler
from .bio import bio_handler
from .tokens import tokens_handler
from .echo import echo_handler

from app.utils.tokens import check_tokens
from app.utils.channel import require_channel_membership
from app.utils.channel import check_membership_callback

from .options.edit_profile import edit_profile_handler

def channel_check(register_func):
    @wraps(register_func)
    def wrapper(app, *args, **kwargs):
        app.add_handler(CommandHandler("start", start_handler))
        app.add_handler(CallbackQueryHandler(check_membership_callback, pattern="^check_membership$"))

        handlers = {
            "bio": bio_handler,
            "help": help_handler,
            "tokens": tokens_handler,
        }
        for command, handler in handlers.items():
            app.add_handler(CommandHandler(command, require_channel_membership(handler)))
        
        # Register options handlers separately
        app.add_handler(edit_profile_handler)
        
        # Premium handlers
        premium_handlers = [
            # (MessageHandler(filters.TEXT & ~filters.COMMAND, check_tokens(0.25)(require_channel_membership(echo_handler)))),
        ]
        
        for handler in premium_handlers:
            app.add_handler(handler)
            
    return wrapper

@channel_check
def register_handlers(app):
    pass