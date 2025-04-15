# app.bot.handlers.__init__.py
from functools import wraps

from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.bot.handlers.start import profile_callback_handler
from app.utils.channel import (
    check_membership_callback,
    require_channel_membership,
)
from app.utils.flags import require_flag
from app.utils.jalali import calendar_callback
from app.utils.tokens import check_tokens

from .bio import bio_handler
from .calendar import calendar_handler
from .echo import echo_handler
from .help import help_handler
from .menu import menu_handler
from .options.edit_profile import edit_profile_handler
from .start import start_handler
from .time import time_handler
from .upload import upload_handler
from .wallet import wallet_handler


def channel_check(register_func):
    @wraps(register_func)
    def wrapper(app, *args, **kwargs):
        # Register options handlers separately
        app.add_handler(edit_profile_handler)

        app.add_handler(CommandHandler("start", start_handler))
        app.add_handler(
            CallbackQueryHandler(
                check_membership_callback, pattern="^check_membership$"
            )
        )
        app.add_handler(
            CallbackQueryHandler(
                profile_callback_handler,
                pattern="^(uni_|fac_|maj_|role_|reset_profile|confirm_reset|cancel_reset|back_university|back_faculty_|back_major|cancel_profile)",
            )
        )
        app.add_handler(CallbackQueryHandler(calendar_callback))
        app.add_handler(upload_handler)

        handlers = {
            "bio": bio_handler,
            "help": help_handler,
            "menu": menu_handler,
            "time": time_handler,
            "calendar": calendar_handler,
            "wallet": wallet_handler,
        }
        for command, handler in handlers.items():
            app.add_handler(
                CommandHandler(command, require_channel_membership(handler))
            )

        # Premium handlers
        premium_handlers = [
            (
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    check_tokens(5)(require_channel_membership(echo_handler)),
                )
            ),
        ]

        # Flag-restricted handlers
        flag_handlers = {
            "wallet": wallet_handler,
            "upload": upload_handler,
        }
        for command, handler in flag_handlers.items():
            app.add_handler(
                CommandHandler(
                    command, require_flag(require_channel_membership(handler))
                )
            )

        for handler in premium_handlers:
            app.add_handler(handler)

    return wrapper


@channel_check
def register_handlers(app):
    pass
