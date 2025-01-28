# app/bot/handlers.py

from telegram import Update
from telegram.ext import ContextTypes
from app.bot.context import DatabaseContext
from sqlalchemy import select
from app.database.models import User
from datetime import datetime
from app.config import Config
import logging

# Configure logging
Config.setup_logging()
logger = logging.getLogger(__name__)

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user is None:
        logger.error("No effective user in the update")
        return

    async with context.db.session() as session:
        result = await session.execute(
            select(User).where(User.t_id == user.id)
        )
        db_user = result.scalar_one_or_none()

        # Get user's profile photos
        photos = await context.bot.get_user_profile_photos(user.id, limit=1)
        photo_id = photos.photos[0][0].file_id if photos and photos.photos else None

        if not db_user:
            db_user = User(
                t_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                profile_id=photo_id
            )
            session.add(db_user)
            welcome_message = (
                f"👋 Welcome {user.first_name}!\n\n"
                f"I'm glad to have you here. You can use /help to see available commands."
            )
        else:
            db_user.last_interaction = datetime.utcnow()
            db_user.username = user.username
            db_user.first_name = user.first_name
            db_user.last_name = user.last_name
            db_user.profile_id = photo_id
            welcome_message = (
                f"👋 Welcome back {user.first_name}!\n\n"
                f"Good to see you again. Need help? Use /help command."
            )
        await session.commit()

    await update.message.reply_text(welcome_message)
    logger.info(f"User interaction: {user.id} - {user.first_name} - {'new user' if not db_user else 'returning user'}")

async def bio_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user is None:
        logger.error("No effective user in the update")
        return

    async with context.db.session() as session:
        result = await session.execute(
            select(User).where(User.t_id == user.id)
        )
        db_user = result.scalar_one_or_none()

        if not db_user:
            await update.message.reply_text("You haven't registered yet. Please use /start first!")
            return

        bio_text = (
            f"👤 *Your Profile Information:*\n\n"
            f"*ID:* `{db_user.t_id}`\n"
            f"*Username:* @{db_user.username or 'Not set'}\n"
            f"*First Name:* {db_user.first_name or 'Not set'}\n"
            f"*Last Name:* {db_user.last_name or 'Not set'}\n"
            f"*Joined:* {db_user.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"*Last Active:* {db_user.last_interaction.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        if db_user.profile_id:
            # Send profile photo with caption
            await update.message.reply_photo(
                photo=db_user.profile_id,
                caption=bio_text,
                parse_mode='Markdown'
            )
        else:
            # Send text only if no profile photo
            await update.message.reply_text(bio_text, parse_mode='Markdown')
            
        logger.info(f"Bio requested by user: {user.id}")

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Help command not implemented yet.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo the user message."""
    if update.message and update.message.text:
        logger.info(f"Received message from {update.effective_user.id}: {update.message.text}")
        await update.message.reply_text(update.message.text)
    else:
        logger.warning(f"Received update without message text: {update}")
