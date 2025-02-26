# app.bot.handlers.start.py
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy import select

from app.database.models import User

import logging

logger = logging.getLogger(__name__)

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user is None:
        logger.error("System: No effective user in the update")
        return

    async with context.db.session() as session:
        result = await session.execute(select(User).where(User.telegram_id == user.id))
        db_user = result.scalar_one_or_none()

        # Get user's profile
        photos = await context.bot.get_user_profile_photos(user.id, limit=1)
        photo_id = (photos.photos[0][0].file_id if photos and photos.photos else None)

        if not db_user:
            # Add user to database
            db_user = User(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                profile=photo_id,
            )
            session.add(db_user)
            welcome_message = (
                f">پنل خوشامدگویی\n"
                f"\n\n✨ *درود و خوش آمدی،‌ {user.first_name} عزیز\!* ✨\n\n"
                f"🎓 *دستیار دانشگاهی شما اینجاست\!*\n"
                f"    ربات دستیار دانشگاه ملی مهارت مازندران، همراه دانشجویان برای مدیریت امور دانشگاهی و دسترسی سریع به اطلاعات و منابع است\.\n\n"
                f"🚀 *دستورات اصلی ربات:*\n"
                f"    🔹 /menu \- مشاهده امکانات\n"
                f"    🔹 /help \- راهنمای استفاده\n"
                f"    🔹 /bio \- مشاهده پروفایل دانشجویی\n"
                f"    🔹 /tokens \- اعتبار دانشجویی\n"
                f"    🔹 /schedule \- مشاهده برنامه هفتگی\n"
                f"    🔹 /reminder \- یادآوری\n"
                f"    🔹 /groups \- جامعه دانشجویی\n\n"
                f"🛟 *آپدیت جدید \[v1\.0\] – بهبودها و ویژگی‌های تازه\!*\n"
                f"    ✅ ایجاد و شخصی سازی پورفایل دانشجویی\n"
                f"    ✅ امکان مشاهده اعتبار دانشجویی\n"
                f"    ✅ امکان مشاهده برنامه هفتگی\n"
                f"    ✅ امکان مشاهده جامعه دانشجویی\n"
                f"    ✅ امکان ایجاد یادآوری\n"
                f"    ✅ امکان مشاهده اطلاعیه‌های دانشگاه\n\n"
                f"**>*توجه:* برای استفاده از این ربات باید در کانال انجمن ما عضو شوید\! \@acm\_nus\n"
            )

        else:
            db_user.last_interaction = datetime.utcnow()
            db_user.username = user.username
            db_user.first_name = user.first_name
            db_user.last_name = user.last_name
            db_user.profile = photo_id
            welcome_message = (
                f">پنل خوشامدگویی\n"
                f"\n\n✨ *خوش برگشتی، {user.first_name} عزیز\!* ✨\n"
                f"    ربات دستیار دانشگاه ملی مهارت مازندران، همراه دانشجویان برای مدیریت امور دانشگاهی و دسترسی سریع به اطلاعات و منابع است\.\n\n"
                f"🚀 *دستورات اصلی ربات:*\n"
                f"    🔹 /menu \- مشاهده امکانات\n"
                f"    🔹 /help \- راهنمای استفاده\n"
                f"    🔹 /bio \- مشاهده پروفایل دانشجویی\n"
                f"    🔹 /tokens \- اعتبار دانشجویی\n"
                f"    🔹 /schedule \- مشاهده برنامه هفتگی\n"
                f"    🔹 /reminder \- یادآوری\n"
                f"    🔹 /groups \- جامعه دانشجویی\n\n"
                f"🛟 *آپدیت جدید \[v1\.0\] – بهبودها و ویژگی‌های تازه\!*\n"
                f"    ✅ ایجاد و شخصی سازی پورفایل دانشجویی\n"
                f"    ✅ امکان مشاهده اعتبار دانشجویی\n"
                f"    ✅ امکان مشاهده برنامه هفتگی\n"
                f"    ✅ امکان مشاهده جامعه دانشجویی\n"
                f"    ✅ امکان ایجاد یادآوری\n"
                f"    ✅ امکان مشاهده اطلاعیه‌های دانشگاه\n\n"
                f"**>*توجه:* برای استفاده از این ربات باید در کانال انجمن ما عضو شوید\! \@acm\_nus\n"
            )
        await session.commit()

        # Create inline keyboard with buttons
        keyboard = [
            [InlineKeyboardButton("🕹️ آموزش ربات دستیار", callback_data="status")],
            [InlineKeyboardButton("🪴 درباره ما", callback_data="status")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_photo(
            photo="AgACAgQAAxkDAAIDS2e5-xgWr1Q44y1XD4sptI38U-eQAALLxzEbwyPQUQZkjCRRddscAQADAgADdwADNgQ",
            caption=welcome_message,
            reply_markup=reply_markup,
            parse_mode="MarkdownV2"
        )
    logger.info(
        f"User interaction: {user.id} - {user.first_name} - {'new user' if not db_user else 'returning user'}"
    )
