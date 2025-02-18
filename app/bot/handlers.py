# app/bot/handlers.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.bot.context import DatabaseContext
from sqlalchemy.ext.asyncio import AsyncSession
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
            select(User).where(User.telegram_id == user.id)
        )
        db_user = result.scalar_one_or_none()

        # Get user's profile photos
        photos = await context.bot.get_user_profile_photos(user.id, limit=1)
        photo_id = photos.photos[0][0].file_id if photos and photos.photos else None

        if not db_user:
            db_user = User(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                profile=photo_id
            )
            session.add(db_user)
            welcome_message = (
                f"✨ خوش آمدید {user.first_name} عزیز ✨\n\n"
                f"🎓 به ربات هوشمند دانشگاه ملی مهارت استان مازندران خوش آمدید!\n\n"
                f"🎯 برای مشاهده امکانات ربات دستور /help را ارسال کنید\n"
                f"💎 برای مشاهده پروفایل خود دستور /bio را ارسال کنید\n"
                f"📊 برای مشاهده اعتبار باقیمانده دستور /tokens را ارسال کنید\n\n"
                f"🌟 با آرزوی موفقیت برای شما 🌟"
            )
        else:
            db_user.last_interaction = datetime.utcnow()
            db_user.username = user.username
            db_user.first_name = user.first_name
            db_user.last_name = user.last_name
            db_user.profile = photo_id
            welcome_message = (
                f"✨ به به! چه کسی اینجاست! {user.first_name} عزیز ✨\n\n"
                f"🌸 خوشحالیم که دوباره به ربات دانشگاه ملی مهارت مازندران برگشتید\n\n"
                f"🎯 برای مشاهده امکانات: /help\n"
                f"👤 مشاهده پروفایل: /bio\n"
                f"💎 موجودی اعتبار: /tokens\n\n"
                f"🍀 روزگارتون پر از موفقیت 🌟"
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
            select(User).where(User.telegram_id == user.id)
        )
        db_user = result.scalar_one_or_none()

        if not db_user:
            await update.message.reply_text("You haven't registered yet. Please use /start first!")
            return

        bio_text = (
f"""
✨ *به پروفایل تبرسکیل‌بات خوش آمدید* ✨\n
    🔸 *نام کاربری*: @{db_user.username or 'تنظیم نشده'}\n
    👤 *اطلاعات شخصی:*
        🧩 *نام:* {db_user.first_name or '—'}
        🧩 *نام خانوادگی:* {db_user.last_name or '—'}
        📱 *شماره تماس:* {db_user.phone or '—'}\n\n
    🎓 *اطلاعات تحصیلی:*
        🔢 *شماره دانشجویی:* {db_user.university_id or '—'}
        🏛️ *دانشکده:* {db_user.faculty or '—'}
        📚 *رشته تحصیلی:* {db_user.major or '—'}
        🗓️ *سال ورود:* {db_user.entry_year or '—'}\n\n
    💎 *وضعیت اشتراک:* {'✨ ویژه' if db_user.is_premium else '🔹 رایگان'}
    📅 *تاریخ ثبت‌نام:* {db_user.created_at.strftime('%y/%m/%d %H:%M')}
    ⏱️ *آخرین فعالیت:* {db_user.last_interaction.strftime('%y/%m/%d %H:%M')}\n
"""
        )

        if db_user.profile:
            # Create inline keyboard with buttons
            keyboard = [
                
                [InlineKeyboardButton("✏️ ویرایش اطلاعات", callback_data="edit_profile")],
                [InlineKeyboardButton("💎 وضعیت اشتراک", callback_data="stats")],
                [InlineKeyboardButton("📢 دعوت دوستان", callback_data="edit_profile")],
                [InlineKeyboardButton("❓ پشتیبانی", callback_data="stats")],
                
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_photo(
                photo=db_user.profile,
                caption=bio_text,
                parse_mode='MarkdownV2',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(bio_text, parse_mode='MarkdownV2')
            
        logger.info(f"Bio requested by user: {user.id}")

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Help command not implemented yet.")

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
            f"""💎 برای خرید توکن بیشتر از دستور /premium استفاده کنید"""
        )
        
        await update.message.reply_text(tokens_message, parse_mode='Markdown')

def check_tokens(cost: float = 0.75):
    def decorator(func):
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
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
                    await update.message.reply_text("Please use /start first!")
                    return

                if db_user.tokens < cost:
                    await update.message.reply_text(
                        f"⚠️ *موجودی ناکافی!*\n\n"
                        f"💰 *اعتبار مورد نیاز:* {str(cost)} *توکن*\n"
                        f"👛 *موجودی شما:* {str(db_user.tokens)} *توکن*\n\n"
                        f"✨ برای افزایش اعتبار و استفاده از امکانات ویژه:\n"
                        f"🎁 دستور /premium را ارسال کنید",
                        parse_mode='Markdown'
                    )
                    return

                db_user.tokens -= cost
                await session.commit()
                return await func(update, context, *args, **kwargs)

        return wrapper
    return decorator

@check_tokens(10)
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo the user message."""
    if update.message and update.message.text:
        logger.info(f"Received message from {update.effective_user.id}: {update.message.text}")
        await update.message.reply_text(update.message.text)
    else:
        logger.warning(f"Received update without message text: {update}")
