# app.bot.handlers.bio.py
import logging

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.database.models import (
    ProfileModel,
    RoleType,
)
from app.utils.jalali import jcal

logger = logging.getLogger(__name__)


def escape_markdown(text):
    special_chars = [
        "_",
        "*",
        "[",
        "]",
        "(",
        ")",
        "~",
        "`",
        ">",
        "#",
        "+",
        "-",
        "=",
        "|",
        "{",
        "}",
        ".",
        "!",
    ]
    for char in special_chars:
        text = str(text).replace(char, f"\{char}")
    return text


async def bio_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    user = update.effective_user
    if user is None:
        logger.error("SYSTEM: No effective user in the update")
        return

    try:
        async with context.db.session() as session:
            # Load profile with student and professor relationships
            result = await session.execute(
                select(ProfileModel)
                .where(ProfileModel.telegram_id == str(user.id))
                .options(selectinload(ProfileModel.student))
                .options(selectinload(ProfileModel.professor))
            )
            db_user = result.scalar_one_or_none()

            if not db_user:
                await update.message.reply_text(
                    "❌ شما هنوز ثبت‌نام نکرده‌اید. لطفا ابتدا از دستور /start استفاده کنید!"
                )
                return

            # Common profile information
            bio_text = (
                f">پروفایل {'دانشجویی' if db_user.role == RoleType.STUDENT else 'استادی'}\n"
                f"\n\n🔸 *‍نام کاربری*: \@{escape_markdown(db_user.telegram_username or 'کاربر جدید')}\n\n"
                f"👤 *اطلاعات شخصی:*\n"
                f"    🧩 نام‌ونام‌خانوادگی: {escape_markdown(db_user.first_name or '—')} {escape_markdown(db_user.last_name or '—')}\n"
                f"    📱 شماره تماس: {escape_markdown(db_user.phone or '—')}\n\n"
            )

            # Role-specific information
            if db_user.role == RoleType.STUDENT and db_user.student:
                bio_text += (
                    f"🎓 *اطلاعات تحصیلی:*\n"
                    f"    🔢 شماره دانشجویی: {escape_markdown(str(db_user.student.student_id) or '—')}\n"
                    f"    🏛️ دانشکده: {escape_markdown(db_user.faculty_name or '⚡️ نیاز به تکمیل')}\n"
                    f"    📚 رشته تحصیلی: {escape_markdown(db_user.major_name or '⚡️ نیاز به تکمیل')}\n"
                    f"    🗓️ سال ورود: {escape_markdown(str(db_user.student.enter_year) or '—')}\n"
                    f"    🏠 خوابگاه: {'دارم' if db_user.student.dormitory else 'ندارم'}\n\n"
                )
            elif db_user.role == RoleType.PROFESSOR and db_user.professor:
                bio_text += (
                    f"👨‍🏫 *اطلاعات استادی:*\n"
                    f"    🏛️ دانشکده: {escape_markdown(db_user.faculty_name or '⚡️ نیاز به تکمیل')}\n"
                    f"    📚 گروه آموزشی: {escape_markdown(db_user.major_name or '⚡️ نیاز به تکمیل')}\n"
                    f"    🎖️ مرتبه علمی: {escape_markdown(str(db_user.professor.position.value) or '—')}\n\n"
                )

            # Common footer information
            bio_text += (
                f"💎 *وضعیت اشتراک:*\n"
                f"    📅 تاریخ ثبت‌نام: {escape_markdown(jcal.format(jcal.tab(db_user.date_created), date_only=True))}\n"
                f"    ⏱️ آخرین فعالیت: {escape_markdown(jcal.format(jcal.tab(db_user.date_updated)) if db_user.date_updated else '—')}\n\n"
                f"**>[چرا برای دستیار دانشگاهی اشتراک ويژه نیاز است؟**](tg://user?id=5455523252)\n\n"
                f"**>[راهنمای استفاده از ربات دستیار**](tg://user?id=5455523252)\n\n"
                f"**>[دسترسی به پشتیبانی فنی ربات دستیار**](tg://user?id=5455523252)\n"
            )

            # Create inline keyboard with buttons
            keyboard = [
                [
                    InlineKeyboardButton(
                        "✏️ ویرایش اطلاعات", callback_data="edit_profile"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "💎 وضعیت اشتراک", callback_data="show_status"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "📢 دعوت دوستان", callback_data="invite"
                    )
                ],
                [InlineKeyboardButton("❓ پشتیبانی", callback_data="support")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            if db_user.telegram_picture:
                await update.message.reply_photo(
                    photo=db_user.telegram_picture,
                    caption=bio_text,
                    parse_mode="MarkdownV2",
                    reply_markup=reply_markup,
                )
            else:
                await update.message.reply_text(
                    bio_text, parse_mode="MarkdownV2", reply_markup=reply_markup
                )

            logger.info(f"Bio requested by user: {user.id}")
    except Exception as e:
        logger.error(f"Error in bio handler: {e}", exc_info=True)
        await update.message.reply_text(
            "خطایی رخ داد. لطفا بعدا دوباره تلاش کنید."
        )
