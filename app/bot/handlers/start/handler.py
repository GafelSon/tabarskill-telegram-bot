# start hander function

# main lib
from datetime import datetime

# dependencies lib
from telegram.ext import ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

# local lib
from app.core.decor import effectiveUser
from app.core.log import internal_error
from app.core.logger import logger
from app.utils.escape import markdownES
from app.database.models import ProfileModel, RoleType
from .profile import start_profile_completion

# config logger
logger = logger(__name__)

@effectiveUser
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        welcome_message = ""
        reply_markup = None
        db_user = None

        async with context.db.session() as session:
            result = await session.execute(select(ProfileModel).where(ProfileModel.telegram_id == str(user.id)))
            db_user = result.scalar_one_or_none()
            if not db_user:
                photos = await context.bot.get_user_profile_photos(user.id, limit=1)
                photo_id = (
                    photos.photos[0][0].file_id
                    if photos and photos.photos
                    else None
                )

                # Create new user for first intraction
                db_user = ProfileModel(
                    telegram_id=str(user.id),
                    telegram_username=user.username or "",
                    telegram_picture=photo_id,
                    # Profile Information
                    first_name=user.first_name or "",
                    last_name=user.last_name or "",
                    # Role Setup
                    role=RoleType.STUDENT,
                    flag=False,
                    university_id=None,
                    profile_completed=False,
                )
                session.add(db_user)
                await session.commit()
                return await start_profile_completion(update, context, db_user)

            elif not db_user.profile_completed:
                db_user.date_updated = datetime.now()
                db_user.telegram_username = user.username or ""
                db_user.first_name = user.first_name or ""
                db_user.last_name = user.last_name or ""
                photos = await context.bot.get_user_profile_photos(
                    user.id, limit=1
                )
                photo_id = (
                    photos.photos[0][0].file_id
                    if photos and photos.photos
                    else None
                )
                db_user.telegram_picture = photo_id
                await session.commit()
                return await start_profile_completion(update, context, db_user)

            else:
                db_user.date_updated = datetime.now()
                db_user.telegram_username = user.username or ""
                db_user.first_name = user.first_name or ""
                db_user.last_name = user.last_name or ""
                photos = await context.bot.get_user_profile_photos(
                    user.id, limit=1
                )
                photo_id = (
                    photos.photos[0][0].file_id
                    if photos and photos.photos
                    else None
                )
                db_user.telegram_picture = photo_id
                await session.commit()

                onboarding = (
                    f">پنل خوشامدگویی\n"
                    f"\n\n✨ *خوش برگشتی، {user.first_name} عزیز\!* ✨\n"
                    f"    ربات دستیار دانشگاه ملی مهارت مازندران، همراه شما برای مدیریت امور دانشگاهی و دسترسی سریع به اطلاعات و منابع است\.\n\n"
                    f"🚀 *دستورات اصلی ربات:*\n"
                    f"    🔹 /menu \- مشاهده امکانات\n"
                    f"    🔹 /help \- راهنمای استفاده\n"
                    f"    🔹 /bio \- مشاهده پروفایل\n"
                    f"    🔹 /wallet \- اعتبار کاربری\n"
                    f"    🔹 /schedule \- مشاهده برنامه هفتگی\n"
                    f"    🔹 /reminder \- یادآوری\n"
                    f"    🔹 /groups \- جامعه دانشگاهی\n\n - دردست توسعه\.\.\."
                    f"🛟 *آپدیت جدید \[v1\.0\] – بهبودها و ویژگی‌های تازه\!*\n"
                    f"    ✅ ایجاد و شخصی سازی پورفایل\n"
                    f"    ✅ امکان مشاهده اعتبار کاربری\n"
                    f"    ✅ امکان مشاهده برنامه هفتگی\n"
                    f"    ✅ امکان مشاهده جامعه دانشگاهی\n"
                    f"    ✅ امکان ایجاد یادآوری\n"
                    f"    ✅ امکان مشاهده اطلاعیه‌های دانشگاه\n\n"
                    f"**>*توجه:* برای استفاده از این ربات باید در کانال انجمن ما عضو شوید\! \@acm\_nus\n"
                )
                logger.info(f"SYSTEM:: StartHandler:: {user.id}-{user.username} returned")

            keyboard = [
                [InlineKeyboardButton("🕹️ آموزش ربات دستیار", callback_data="tutorial")],
                [InlineKeyboardButton("🪴 درباره ما", callback_data="about")],
                [InlineKeyboardButton("🔄 تنظیم مجدد حساب", callback_data="reset_profile")],
            ]
            keyboard_layout = InlineKeyboardMarkup(keyboard)
            canvas = "AgACAgQAAyEGAASLt5ydAAMmZ_yo0BP-GMN8Vjv7pn9FojWPr4IAAnDGMRstPuFT2ygGVy3kLJ8BAAMCAANtAAM2BA"

            if update.message:
                await update.message.reply_photo(
                    photo=canvas,
                    caption=onboarding,
                    reply_markup=keyboard_layout,
                    parse_mode="MarkdownV2",
                )
    except Exception as e:
        logger.error(f"SYSTEM:: StartHandler:: {e}", exc_info=True)
        if update.message:
            await update.message.reply_text(internal())