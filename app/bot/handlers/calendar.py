# calendar handler


# main lib
# .
# .

# dependencies lib
from telegram import Update, Message
from telegram.ext import ContextTypes

# local lib
from app.core.logger import logger
from app.core.decor import message_object

# logger config
logger = logger(__name__)


@message_object
async def handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE, message: Message = None
) -> None:
    # _, calendar_markup = calendar.get_month_calendar()
    await message.reply_photo(
        photo="AgACAgQAAyEGAASLt5ydAAN3aDwGRc9FFmNRzOFNgnJZpkSafksAAtrGMRukluBR-rIn0c60ifYBAAMCAAN5AAM2BA",
        caption="کارگران مشغول کارند",
        parse_mode="MarkdownV2",
    )
