# bio handler function

# main lib
# .
# .

# dependencies lib
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from telegram.ext import ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

# local lib
from app.core.log import start_warning, internal_error
from app.core.logger import logger
from app.core.decor import effectiveUser
from app.utils.jalali import jcal
from app.utils.escape import markdownES as mds
from app.database.models import (
    ProfileModel,
    RoleType,
)

# config logger
logger = logger(__name__)


@effectiveUser
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    try:
        async with context.db.session() as session:
            result = await session.execute(
                select(ProfileModel)
                .where(ProfileModel.telegram_id == str(user.id))
                .options(selectinload(ProfileModel.student))
                .options(selectinload(ProfileModel.professor))
            )
            db_user = result.scalar_one_or_none()

            if not db_user:
                await update.message.reply_text(start_warning())
                return

            onboarding = (
                f">پروفایل {'دانشجویی' if db_user.role == RoleType.STUDENT else 'استادی'}\n"
                f"\n\n🔸 *‍نام کاربری*: \@{mds(db_user.telegram_username or 'کاربر جدید')}\n\n"
                f"👤 *اطلاعات شخصی:*\n"
                f"    🧩 نام‌ونام‌خانوادگی: {mds(db_user.first_name or '—')} {mds(db_user.last_name or '—')}\n"
                f"    📱 شماره تماس: {mds(db_user.phone or '—')}\n\n"
            )

            if db_user.role == RoleType.STUDENT and db_user.student:
                onboarding += (
                    f"🎓 *اطلاعات تحصیلی:*\n"
                    f"    🔢 شماره دانشجویی: {mds(str(db_user.student.student_id) or '—')}\n"
                    f"    🏛️ دانشکده: {mds(db_user.faculty_name or '⚡️ نیاز به تکمیل')}\n"
                    f"    📚 رشته تحصیلی: {mds(db_user.major_name or '⚡️ نیاز به تکمیل')}\n"
                    f"    🗓️ سال ورود: {mds(str(db_user.student.enter_year) or '—')}\n"
                    f"    🏠 خوابگاه: {'دارم' if db_user.student.dormitory else 'ندارم'}\n\n"
                )
            elif db_user.role == RoleType.PROFESSOR and db_user.professor:
                onboarding += (
                    f"👨‍🏫 *اطلاعات استادی:*\n"
                    f"    🏛️ دانشکده: {mds(db_user.faculty_name or '⚡️ نیاز به تکمیل')}\n"
                    f"    📚 گروه آموزشی: {mds(db_user.major_name or '⚡️ نیاز به تکمیل')}\n"
                    f"    🎖️ مرتبه علمی: {mds(str(db_user.professor.position.value) or '—')}\n\n"
                )

            onboarding += (
                f"💎 *تاریخچه:*\n"
                f"    📅 تاریخ ثبت‌نام: {mds(jcal.format(jcal.tab(db_user.date_created), date_only=True))}\n"
                f"    ⏱️ آخرین فعالیت: {mds(jcal.format(jcal.tab(db_user.date_updated)) if db_user.date_updated else '—')}\n\n"
                f"**>[چرا برای دستیار دانشگاهی اشتراک ويژه نیاز است؟**](tg://user?id=5455523252)\n\n"
                f"**>[راهنمای استفاده از ربات دستیار**](tg://user?id=5455523252)\n\n"
                f"**>[دسترسی به پشتیبانی فنی ربات دستیار**](tg://user?id=5455523252)\n"
            )

            keyboard = [
                [
                    InlineKeyboardButton(
                        "✏️ ویرایش اطلاعات", callback_data="edit_profile"
                    )
                ],
                [InlineKeyboardButton("💼 کیف پول", callback_data="show_status")],
                [InlineKeyboardButton("📢 دعوت دوستان", callback_data="invite")],
                [InlineKeyboardButton("❓ پشتیبانی", callback_data="support")],
            ]
            keyboard_layout = InlineKeyboardMarkup(keyboard)

            if db_user.telegram_picture:
                await update.message.reply_photo(
                    photo=db_user.telegram_picture,
                    caption=onboarding,
                    parse_mode="MarkdownV2",
                    reply_markup=keyboard_layout,
                )
            else:
                await update.message.reply_text(
                    onboarding, parse_mode="MarkdownV2", reply_markup=keyboard_layout
                )

            logger.info(f"SYSTEM:: BioHandler:: Bio requested by user: {user.id}")
    except Exception as e:
        logger.error(f"SYSTEM:: BioHandler:: Error in bio handler: {e}", exc_info=True)
        await update.message.reply_text(internal_error())
