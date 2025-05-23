# echo handler function
# THIS IS TEST HANDLER FOR BIGGER PURPOSES

# main lib
# .
# .

# dependencies lib
from telegram import Update
from telegram.ext import ContextTypes

# local lib
from app.core.logger import logger
from app.utils.escape import markdownES as mds
from app.utils.dialog import simple_dialog_manager

# config logger
logger = logger(__name__)


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        user_input = update.message.text
        response = simple_dialog_manager(user_input)
        await update.message.reply_text(text=mds(response), parse_mode="MarkdownV2")
