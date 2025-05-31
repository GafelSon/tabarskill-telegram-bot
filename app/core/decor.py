# decorators functions

# main lib
from functools import wraps

# dependencies lib
from telegram import Update
from telegram.ext import ContextTypes

# local lib
from app.core.logger import logger

# config logger
logger = logger(__name__)


def effectiveUser(func):
    @wraps(func)
    async def wrapper(update, *args, **kwargs):
        user = getattr(update, "effective_user", None)
        if user is None:
            logger.error("SYSTEM: No effective user in the update")
            return
        return await func(update, *args, **kwargs)

    return wrapper


def message_object(func):
    @wraps(func)
    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        message = (
            update.callback_query.message if update.callback_query else update.message
        )
        if message is None:
            logger.error(f"SYSTEM:: {func.__name__}:: No message found in update!")
            return
        
        import inspect
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        
        if len(params) > 2:
            return await func(update, context, message, *args, **kwargs)
        else:
            return await func(update, context, *args, **kwargs)

    return wrapper
