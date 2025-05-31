# start hander function __other__

# main lib
import asyncio
from datetime import datetime

# dependencies lib
from telegram.ext import ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from sqlalchemy import select, delete
from telegram.error import BadRequest

# local lib
from app.core.logger import logger
from app.core.log import internal_error, call_error, celebration_info, start_warning
from app.utils.escape import markdownES
from app.database.models import (
    ProfileModel,
    UniversityModel,
    FacultyModel,
    MajorModel,
    RoleType,
    StudentModel,
    ProfessorModel,
    ProfessorPosType,
)

# config logger
logger = logger(__name__)


async def begin_profile(
    update: Update, context: ContextTypes.DEFAULT_TYPE, user_profile: ProfileModel
) -> None:
    logger.info(
        f"SYSTEM:: StartHandler:: Starting profile completion:: {update.effective_user.id}"
    )

    try:
        if not user_profile.university_id:
            await ask_university(update, context)
        elif not user_profile.faculty_name:
            await ask_faculty(update, context, user_profile.university_id)
        elif not user_profile.major_name:
            await ask_major(update, context, user_profile.faculty_id)
        elif user_profile.role not in [RoleType.STUDENT, RoleType.PROFESSOR]:
            await ask_role(update, context)
        else:
            async with context.db.session() as session:
                # sql query
                result = await session.execute(
                    select(ProfileModel).where(
                        ProfileModel.telegram_id == str(update.effective_user.id)
                    )
                )

                db_user = result.scalar_one_or_none()
                if db_user:
                    db_user.profile_completed = True
                    db_user.date_updated = datetime.now()
                    await session.commit()
                    context.bot_data.setdefault("profile_completions", 0)
                    context.bot_data["profile_completions"] += 1

                    if update.callback_query:
                        await update.callback_query.answer(celebration_info())
    except Exception as e:
        logger.error(
            f"SYSTEM:: StartHandler:: Error in profile completion: {e}", exc_info=True
        )
        if update.message:
            await update.message.reply_text(internal_error())


async def ask_university(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ask University"""
    async with context.db.session() as session:
        result = await session.execute(
            select(UniversityModel).order_by(UniversityModel.name)
        )
        universities = result.scalars().all()

        if not universities:
            message = call_error
            if update.callback_query:
                await update.callback_query.answer(message, show_alert=True)
                return
            elif update.message:
                await update.message.reply_text(message)
                return

        keyboard = []
        if len(universities) > 10:
            current_letter = None
            current_row = []

            for uni in universities:
                first_letter = uni.name[0].upper()
                if first_letter != current_letter:
                    if current_row:
                        keyboard.append(current_row)
                        current_row = []
                    current_letter = first_letter

                callback_data = f"uni_{uni.id}"
                current_row.append(
                    InlineKeyboardButton(f"🏛️ {uni.name}", callback_data=callback_data)
                )
                if len(current_row) == 2:
                    keyboard.append(current_row)
                    current_row = []

            if current_row:
                keyboard.append(current_row)
        else:
            for uni in universities:
                callback_data = f"uni_{uni.id}"
                keyboard.append(
                    [InlineKeyboardButton(f"🏛️ {uni.name}", callback_data=callback_data)]
                )
        keyboard.append(
            [InlineKeyboardButton("❌ لغو", callback_data="cancel_profile")]
        )

        keyboard_layout = InlineKeyboardMarkup(keyboard)
        onboarding = (
            f">🎓 *تکمیل پروفایل \- مرحله ۱ از ۴* 🔖\n\n\n"
            f"👋 *{markdownES(update.effective_user.first_name)} عزیز* ✨\n\n"
            f"🌟 به منظور بهره‌مندی کامل از امکانات و خدمات شخصی‌سازی شده ربات، لطفاً اطلاعات حساب کاربری خود را تکمیل فرمایید\. 📝\n\n"
            f"🏛️ لطفاً دانشگاه خود را انتخاب کنید: 🔍"
        )

        try:
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    onboarding, reply_markup=keyboard_layout, parse_mode="MarkdownV2"
                )
            elif update.message:
                await update.message.reply_text(
                    onboarding, reply_markup=keyboard_layout, parse_mode="MarkdownV2"
                )

        except BadRequest as e:
            logger.warning(f"SYSTEM:: StartHandler:: Other:: ask_university: {e}")
            if update.message:
                await update.message.reply_text(
                    onboarding, reply_markup=keyboard_layout, parse_mode="MarkdownV2"
                )
            elif update.callback_query and update.callback_query.message:
                await update.callback_query.message.reply_text(
                    onboarding, reply_markup=keyboard_layout, parse_mode="MarkdownV2"
                )


async def ask_faculty(
    update: Update, context: ContextTypes.DEFAULT_TYPE, university_id: int
) -> None:
    """Ask Faculty"""
    async with context.db.session() as session:
        result = await session.execute(
            select(UniversityModel).where(UniversityModel.id == university_id)
        )
        university = result.scalar_one_or_none()

        if not university:
            logger.error(
                f"SYSTEM:: StartHandler:: Other:: University with ID {university_id} not found"
            )
            if update.callback_query:
                await update.callback_query.answer(
                    "⚠️ دانشگاه مورد نظر یافت نشد. لطفاً دوباره تلاش کنید.",
                    show_alert=True,
                )
                await ask_university(update, context)
            return

        result = await session.execute(
            select(FacultyModel)
            .where(FacultyModel.university_id == university_id)
            .order_by(FacultyModel.name)
        )
        faculties = result.scalars().all()

        if not faculties:
            if update.callback_query:
                await update.callback_query.answer(
                    "⚠️ برای این دانشگاه دانشکده‌ای ثبت نشده است.",
                    show_alert=True,
                )
                await ask_university(update, context)
            return

        keyboard = []
        current_row = []
        for faculty in faculties:
            callback_data = f"fac_{faculty.id}"
            current_row.append(
                InlineKeyboardButton(f"🔬 {faculty.name}", callback_data=callback_data)
            )
            if len(current_row) == 2 or faculty == faculties[-1]:
                keyboard.append(current_row)
                current_row = []
        keyboard.append(
            [
                InlineKeyboardButton("↩️ بازگشت", callback_data="back_university"),
                InlineKeyboardButton("❌ لغو", callback_data="cancel_profile"),
            ]
        )
        reply_markup = InlineKeyboardMarkup(keyboard)

        onboarding = (
            f">🎓 *تکمیل پروفایل \- مرحله ۲ از ۴* 🔖\n\n\n"
            f"👋 *{markdownES(update.effective_user.first_name)} عزیز* ✨\n\n"
            f"  🏛️ دانشگاه:  *{markdownES(university.name)}* 🎯\n\n"
            f"🔬 لطفاً دانشکده خود را از میان موارد زیر انتخاب کنید: 📋\n"
        )

        try:
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    onboarding, reply_markup=reply_markup, parse_mode="MarkdownV2"
                )
            else:
                if update.message:
                    await update.message.reply_text(
                        onboarding,
                        reply_markup=reply_markup,
                        parse_mode="MarkdownV2",
                    )
        except BadRequest as e:
            logger.warning(f"SYSTEM:: StartHandler:: Other:: Error in ask_faculty: {e}")
            if update.callback_query and update.callback_query.message:
                await update.callback_query.message.reply_text(
                    onboarding, reply_markup=reply_markup, parse_mode="MarkdownV2"
                )


async def ask_major(
    update: Update, context: ContextTypes.DEFAULT_TYPE, faculty_id: int
) -> None:
    """Ask Major"""
    async with context.db.session() as session:
        result = await session.execute(
            select(FacultyModel).where(FacultyModel.id == faculty_id)
        )
        faculty = result.scalar_one_or_none()

        if not faculty:
            logger.error(
                f"SYSTEM:: StartHandler:: Other:: Faculty with ID {faculty_id} not found"
            )
            if update.callback_query:
                await update.callback_query.answer(
                    "⚠️ دانشکده مورد نظر یافت نشد. لطفاً دوباره تلاش کنید.",
                    show_alert=True,
                )
                await ask_university(update, context)
            return
        result = await session.execute(
            select(MajorModel)
            .where(MajorModel.faculty_id == faculty_id)
            .order_by(MajorModel.name)
        )
        majors = result.scalars().all()

        if not majors:
            if update.callback_query:
                await update.callback_query.answer(
                    "⚠️ برای این دانشکده رشته‌ای ثبت نشده است.", show_alert=True
                )
                await ask_faculty(update, context, faculty.university_id)
            return

        keyboard = []
        for major in majors:
            callback_data = f"maj_{major.id}"
            keyboard.append(
                [InlineKeyboardButton(f"📚 {major.name}", callback_data=callback_data)]
            )
        keyboard.append(
            [
                InlineKeyboardButton(
                    "↩️ بازگشت",
                    callback_data=f"back_faculty_{faculty.university_id}",
                ),
                InlineKeyboardButton("❌ لغو", callback_data="cancel_profile"),
            ]
        )

        keyboard_layout = InlineKeyboardMarkup(keyboard)
        uni_result = await session.execute(
            select(UniversityModel).where(UniversityModel.id == faculty.university_id)
        )
        university = uni_result.scalar_one_or_none()
        uni_name = university.name if university else "نامشخص"

        onboarding = (
            f">🎓 *تکمیل پروفایل \- مرحله ۳ از ۴* 🔖\n\n\n"
            f"👋 *{markdownES(update.effective_user.first_name)} عزیز* ✨\n\n"
            f"  🏛️ دانشگاه:  *{markdownES(uni_name)}* 🎯\n"
            f"  🔬 دانشکده:  *{markdownES(faculty.name)}* 📋\n\n"
            f"📚 لطفاً رشته تحصیلی خود را انتخاب کنید: 🔍"
        )

        try:
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    onboarding, reply_markup=keyboard_layout, parse_mode="MarkdownV2"
                )
            else:
                if update.message:
                    await update.message.reply_text(
                        onboarding,
                        reply_markup=keyboard_layout,
                        parse_mode="MarkdownV2",
                    )
        except BadRequest as e:
            logger.warning(f"Error in ask_major: {e}")
            if update.callback_query and update.callback_query.message:
                await update.callback_query.message.reply_text(
                    onboarding, reply_markup=keyboard_layout, parse_mode="MarkdownV2"
                )


async def ask_role(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ask Role (student or professor)"""
    async with context.db.session() as session:
        result = await session.execute(
            select(ProfileModel).where(
                ProfileModel.telegram_id == str(update.effective_user.id)
            )
        )
        user_profile = result.scalar_one_or_none()

        if not user_profile:
            logger.error(
                f"SYSTEM:: StartHandler:: Other:: User profile not found for user {update.effective_user.id}"
            )
            if update.callback_query:
                await update.callback_query.answer(
                    start_warning(),
                    show_alert=True,
                )
            return

    keyboard = [
        [InlineKeyboardButton("👨‍🎓 دانشجو", callback_data="role_student")],
        [InlineKeyboardButton("👨‍🏫 استاد", callback_data="role_professor")],
        [InlineKeyboardButton("↩️ بازگشت", callback_data="back_major")],
        [InlineKeyboardButton("❌ لغو", callback_data="cancel_profile")],
    ]

    keyboard_layout = InlineKeyboardMarkup(keyboard)

    onboarding = (
        f">🎓 *تکمیل پروفایل \- مرحله ۴ از ۴* 🔖\n\n\n"
        f"👋 *{markdownES(update.effective_user.first_name)} عزیز* ✨\n\n"
        f"  🏛️ دانشگاه:  *{markdownES(user_profile.university_name)}* 🎯\n"
        f"  🔬 دانشکده:  *{markdownES(user_profile.faculty_name)}* 📋\n"
        f"  📚 رشته: *{markdownES(user_profile.major_name)}* 🔍\n\n"
        f"👤 لطفاً نقش خود را در دانشگاه انتخاب کنید: 🧑‍🏫"
    )

    try:
        if update.callback_query:
            await update.callback_query.edit_message_text(
                onboarding, reply_markup=keyboard_layout, parse_mode="MarkdownV2"
            )
        else:
            # Fallback if somehow we get here without a callback query
            if update.message:
                await update.message.reply_text(
                    onboarding, reply_markup=keyboard_layout, parse_mode="MarkdownV2"
                )
    except BadRequest as e:
        logger.warning(f"Error in ask_role: {e}")
        if update.callback_query and update.callback_query.message:
            await update.callback_query.message.reply_text(
                onboarding, reply_markup=keyboard_layout, parse_mode="MarkdownV2"
            )


async def welcome(
    update: Update, context: ContextTypes.DEFAULT_TYPE, user_profile: ProfileModel
) -> None:
    """Show welcome message"""
    user = update.effective_user
    onboarding = (
        f">پنل خوشامدگویی\n"
        f"\n\n✨ *درود و خوش آمدی،‌ {markdownES(user.first_name)} عزیز\!* ✨\n\n"
        f"🎓 *به دستیار دانشگاهی خوش آمدید\!*\n"
        f"    ربات دستیار دانشگاه ملی مهارت مازندران، همراه شما برای مدیریت امور دانشگاهی و دسترسی سریع به اطلاعات و منابع است\.\n\n"
        f"📋 *اطلاعات پروفایل شما:*\n"
        f"    🏛️ دانشگاه: {markdownES(user_profile.university_name)}\n"
        f"    🔬 دانشکده: {markdownES(user_profile.faculty_name)}\n"
        f"    📚 رشته: {markdownES(user_profile.major_name)}\n"
        f"    👤 نقش: {'دانشجو' if user_profile.role == RoleType.STUDENT else 'استاد'}\n\n"
        f"🚀 *دستورات اصلی ربات:*\n"
        f"    🔹 /menu \- مشاهده امکانات\n"
        f"    🔹 /help \- راهنمای استفاده\n"
        f"    🔹 /bio \- مشاهده پروفایل\n"
        f"    🔹 /tokens \- اعتبار کاربری\n"
        f"    🔹 /schedule \- مشاهده برنامه هفتگی\n"
        f"    🔹 /reminder \- یادآوری\n"
        f"    🔹 /groups \- جامعه دانشگاهی\n\n"
        f"🛟 *آپدیت جدید \[v1\.0\.12\] \- بهبودها و ویژگی‌های تازه\!*\n"
        f"    ✅ ایجاد و شخصی سازی پروفایل\n"
        f"    ✅ امکان مشاهده اعتبار کاربری\n"
        f"    ✅ امکان مشاهده برنامه هفتگی\n"
        f"    ✅ امکان ایجاد یادآوری\n"
        f"    ✅ امکان مشاهده اطلاعیه‌های دانشگاه\n\n"
        f"**>*توجه:* برای استفاده از این ربات باید در کانال انجمن ما عضو شوید\! \@acm\_nus\n"
    )

    keyboard = [
        [InlineKeyboardButton("🕹️ آموزش ربات دستیار", callback_data="tutorial")],
        [InlineKeyboardButton("🪴 درباره ما", callback_data="about")],
        [InlineKeyboardButton("🔄 تنظیم مجدد حساب", callback_data="reset_profile")],
    ]
    keyboard_layout = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            onboarding, reply_markup=keyboard_layout, parse_mode="MarkdownV2"
        )
    else:
        if update.message:
            await update.message.reply_photo(
                photo="AgACAgQAAyEGAASLt5ydAAMmZ_yo0BP-GMN8Vjv7pn9FojWPr4IAAnDGMRstPuFT2ygGVy3kLJ8BAAMCAANtAAM2BA",
                caption=onboarding,
                reply_markup=keyboard_layout,
                parse_mode="MarkdownV2",
            )


async def callbucket(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle callbacks profile completion"""
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = update.effective_user.id
    logger.debug(
        f"SYSTEM:: StartHandler:: Profile callback received: {data} from user {user_id}"
    )

    async with context.db.session() as session:
        result = await session.execute(
            select(ProfileModel).where(ProfileModel.telegram_id == str(user_id))
        )
        user_profile = result.scalar_one_or_none()

        if not user_profile:
            logger.warning(
                f"SYSTEM:: StartHandler:: User profile not found for user_id {user_id}"
            )
            await query.message.reply_text(
                markdownES(start_warning()),
                parse_mode="MarkdownV2",
            )
            return

        if data == "cancel_profile":
            await query.message.reply_text(
                markdownES(
                    "⚠️ فرآیند تکمیل پروفایل لغو شد. هر زمان که مایل بودید می‌توانید با دستور /start مجدداً شروع کنید."
                ),
                parse_mode="MarkdownV2",
            )
            try:
                await query.message.delete()
            except BadRequest:
                pass
            return

        if data.startswith("back_"):
            if "university" in data:
                await ask_university(update, context)
                return
            elif "faculty" in data:
                university_id = (
                    int(data.split("_")[2])
                    if len(data.split("_")) > 2
                    else user_profile.university_id
                )
                await ask_faculty(update, context, university_id)
                return
            elif "major" in data:
                await ask_major(update, context, user_profile.faculty_id)
                return

        if data == "reset_profile":
            keyboard = [
                [
                    InlineKeyboardButton(
                        "✅ بله، مطمئنم", callback_data="confirm_reset"
                    ),
                    InlineKeyboardButton(
                        "❌ خیر، انصراف", callback_data="cancel_reset"
                    ),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            if hasattr(query.message, "photo") and query.message.photo:
                await query.edit_message_caption(
                    caption=markdownES(
                        "آیا از بازنشانی پروفایل خود مطمئن هستید؟ این عمل غیرقابل بازگشت است."
                    ),
                    reply_markup=reply_markup,
                    parse_mode="MarkdownV2",
                )
            else:
                await query.edit_message_text(
                    markdownES(
                        "آیا از بازنشانی پروفایل خود مطمئن هستید؟ این عمل غیرقابل بازگشت است."
                    ),
                    reply_markup=reply_markup,
                    parse_mode="MarkdownV2",
                )
            return

        if data == "confirm_reset":
            user_profile.university_id = None
            user_profile.university_name = None
            user_profile.faculty_id = None
            user_profile.faculty_name = None
            user_profile.major_id = None
            user_profile.major_name = None
            user_profile.role = RoleType.STUDENT
            user_profile.profile_completed = False
            await session.commit()

            logger.info(f"User {user_id} reset their profile")

            try:
                await query.edit_message_text(
                    markdownES(
                        "🔄 پروفایل شما با موفقیت بازنشانی شد. اکنون فرآیند ثبت‌نام مجدد آغاز می‌شود..."
                    ),
                    parse_mode="MarkdownV2",
                )
                await asyncio.sleep(2)
                await query.message.delete()
            except (BadRequest, Exception) as e:
                logger.warning(f"Error during profile reset: {e}")
                pass

            await begin_profile(update, context, user_profile)
            return
        if data == "cancel_reset":
            await welcome(update, context, user_profile)
            return

        try:
            if data.startswith("uni_"):
                university_id = int(data[4:])
                uni_result = await session.execute(
                    select(UniversityModel).where(UniversityModel.id == university_id)
                )
                university = uni_result.scalar_one_or_none()

                if not university:
                    logger.error(f"University with ID {university_id} not found")
                    await query.message.reply_text(
                        markdownES(
                            "⚠️ دانشگاه انتخاب شده یافت نشد. لطفاً دوباره تلاش کنید."
                        ),
                        parse_mode="MarkdownV2",
                    )
                    return

                user_profile.university_id = university_id
                user_profile.university_name = university.name
                user_profile.faculty_id = None
                user_profile.faculty_name = None
                user_profile.major_id = None
                user_profile.major_name = None
                await session.commit()

                logger.info(f"User {user_id} selected university: {university.name}")
                await ask_faculty(update, context, university_id)

            elif data.startswith("fac_"):
                faculty_id = int(data[4:])
                fac_result = await session.execute(
                    select(FacultyModel).where(FacultyModel.id == faculty_id)
                )
                faculty = fac_result.scalar_one_or_none()

                if not faculty:
                    logger.error(f"Faculty with ID {faculty_id} not found")
                    await query.message.reply_text(
                        markdownES(
                            "⚠️ دانشکده انتخاب شده یافت نشد. لطفاً دوباره تلاش کنید."
                        ),
                        parse_mode="MarkdownV2",
                    )
                    return

                user_profile.faculty_id = faculty_id
                user_profile.faculty_name = faculty.name
                user_profile.major_id = None
                user_profile.major_name = None
                await session.commit()

                logger.info(f"User {user_id} selected faculty: {faculty.name}")
                await ask_major(update, context, faculty_id)

            elif data.startswith("maj_"):
                major_id = int(data[4:])
                maj_result = await session.execute(
                    select(MajorModel).where(MajorModel.id == major_id)
                )
                major = maj_result.scalar_one_or_none()

                if not major:
                    logger.error(f"Major with ID {major_id} not found")
                    await query.message.reply_text(
                        markdownES(
                            "⚠️ رشته انتخاب شده یافت نشد. لطفاً دوباره تلاش کنید."
                        ),
                        parse_mode="MarkdownV2",
                    )
                    return

                user_profile.major_id = major_id
                user_profile.major_name = major.name
                await session.commit()

                logger.info(f"User {user_id} selected major: {major.name}")
                await ask_role(update, context)

            elif data.startswith("role_"):
                role = (
                    RoleType.STUDENT if data == "role_student" else RoleType.PROFESSOR
                )
                user_profile.role = role
                user_profile.profile_completed = True

                await session.execute(
                    delete(StudentModel).where(
                        StudentModel.profile_id == user_profile.id
                    )
                )
                await session.execute(
                    delete(ProfessorModel).where(
                        ProfessorModel.profile_id == user_profile.id
                    )
                )

                if role == RoleType.STUDENT:
                    student = StudentModel(
                        profile_id=user_profile.id,
                        student_id=int(user_profile.telegram_id),
                        enter_year=datetime.now().year,
                        dormitory=False,
                    )
                    session.add(student)
                    role_str = "دانشجو"
                else:
                    professor = ProfessorModel(
                        profile_id=user_profile.id,
                        position=ProfessorPosType.ADJUNCT_PROFESSOR,
                    )
                    session.add(professor)
                    role_str = "استاد"

                await session.commit()

                await query.answer(
                    f"🎉 پروفایل شما با نقش {role_str} با موفقیت تکمیل شد!"
                )
                logger.info(f"User {user_id} completed profile as {role_str}")

                # Record analytics
                try:
                    context.bot_data.setdefault("profile_completions", 0)
                    context.bot_data["profile_completions"] += 1
                except Exception as e:
                    logger.warning(f"Failed to record analytics: {e}")

                await welcome(update, context, user_profile)

            else:
                logger.warning(f"Unknown callback data: {data} from user {user_id}")

        except Exception as e:
            logger.error(f"Error in profile_callback_handler: {e}", exc_info=True)
            try:
                await query.message.reply_text(
                    markdownES(start_warning()),
                    parse_mode="MarkdownV2",
                )
            except Exception:
                pass

            await begin_profile(update, context, user_profile)


__all__ = [
    "begin",
    "ask_university",
    "ask_faculty",
    "ask_major",
    "ask_role",
    "welcome",
    "callbucket",
]
