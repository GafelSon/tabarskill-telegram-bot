from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy import select
from app.database.models import User
import logging

logger = logging.getLogger(__name__)

async def tokens_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user is None:
        logger.error("No effective user in the update")
        return

    async with context.db.session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user.id)
        )
        db_user = result.scalar_one_or_none()

        if not db_user:
            await update.message.reply_text("⚠️ لطفا ابتدا دستور /start را ارسال کنید")
            return

        # Escape the decimal
        tokens_message = (
            f"""💰 *موجودی فعلی شما:* {str(db_user.tokens)} *توکن* ✨\n\n"""
            f"""💎 برای خرید توکن بیشتر از دستور /tokens استفاده کنید"""
        )
        
        await update.message.reply_text(tokens_message, parse_mode='Markdown')