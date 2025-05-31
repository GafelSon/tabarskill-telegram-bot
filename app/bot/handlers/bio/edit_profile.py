# bio handler -> edit profile

# main lib
import asyncio
import logging

# dependencies lib
from sqlalchemy import select
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# local lib
from app.core.logger import logger
from app.core.log import start_warning, internal_error, call_error
from app.bot.handlers.bio import handler as bio_handler
from app.database.models import ProfileModel, RoleType, StudentModel

# logger config
logger = logger(__name__)

(
    FIRST_NAME,
    LAST_NAME,
    PHONE,
    EMAIL,
    STUDENT_ID,
    ENTRY_YEAR,
    DORMITORY,
    PHOTO,
) = range(8)


def get_keyboard():
    return ReplyKeyboardMarkup(
        [["قبلی ◀️", "▶️ بعدی"], ["🚫 انصراف"]], resize_keyboard=True
    )


def get_entry_year_keyboard():
    keyboard = [
        ["1400", "1401", "1402"],
        ["1403", "1404"],
        ["قبلی ◀️", "▶️ بعدی"],
        ["🚫 انصراف"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_dormitory_keyboard():
    keyboard = [["بله", "خیر"], ["قبلی ◀️", "▶️ بعدی"], ["🚫 انصراف"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


QUESTIONS = {
    FIRST_NAME: "👤 لطفاً نام خود را وارد کنید:",
    LAST_NAME: "👥 لطفاً نام خانوادگی خود را وارد کنید:",
    PHONE: "📱 لطفاً شماره تماس خود را وارد کنید:",
    EMAIL: "📧 لطفاً ایمیل خود را وارد کنید:",
    STUDENT_ID: "🎓 لطفاً شماره دانشجویی خود را وارد کنید:",
    ENTRY_YEAR: "📅 لطفاً سال ورود خود را وارد کنید:",
    DORMITORY: "🏠 آیا ساکن خوابگاه هستید؟ (بله/خیر)",
    PHOTO: "🖼️ لطفاً عکس پروفایل خود را ارسال کنید:",
}

FIELDS = {
    FIRST_NAME: "first_name",
    LAST_NAME: "last_name",
    PHONE: "phone",
    EMAIL: "email",
    STUDENT_ID: "student_id",
    ENTRY_YEAR: "enter_year",
    DORMITORY: "dormitory",
    PHOTO: "telegram_picture",
}


async def start_profile_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        logger.info(f"Starting profile edit for user: {update.effective_user.id}")
        await update.callback_query.answer()
        async with context.db.session() as session:
            result = await session.execute(
                select(ProfileModel).where(
                    ProfileModel.telegram_id == str(update.effective_user.id)
                )
            )
            profile = result.scalar_one_or_none()

            if not profile:
                await update.callback_query.message.reply_text(
                    start_warning(),
                    reply_markup=ReplyKeyboardRemove(),
                )
                return ConversationHandler.END

            context.user_data["profile_id"] = profile.id
            context.user_data["role"] = profile.role

        context.user_data[
            "edit_message"
        ] = await update.callback_query.message.reply_text(
            QUESTIONS[FIRST_NAME], reply_markup=get_keyboard()
        )
        context.user_data["current_state"] = FIRST_NAME
        return FIRST_NAME

    except Exception as e:
        logger.error(f"Error in start_profile_edit: {str(e)}", exc_info=True)
        await update.callback_query.message.reply_text(
            internal_error(),
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END


async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        if "user_messages" not in context.user_data:
            context.user_data["user_messages"] = []
        context.user_data["user_messages"].append(update.message)

        current_state = context.user_data.get("current_state", FIRST_NAME)
        text = update.message.text

        if "edit_message" in context.user_data:
            await context.user_data["edit_message"].delete()

        if text == "قبلی ◀️":
            if current_state == FIRST_NAME:
                return await cancel(update, context)
            next_state = current_state - 1
            context.user_data["edit_message"] = await update.message.reply_text(
                QUESTIONS[next_state], reply_markup=get_keyboard()
            )
            context.user_data["current_state"] = next_state
            return next_state

        if text == "🚫 انصراف":
            return await cancel(update, context)

        field_name = FIELDS[current_state]
        if text != "▶️ بعدی":
            if current_state == PHONE and not text.isdigit():
                await update.message.reply_text(
                    "❌ شماره تلفن باید فقط شامل اعداد باشد."
                )
                context.user_data["edit_message"] = await update.message.reply_text(
                    QUESTIONS[current_state], reply_markup=get_keyboard()
                )
                return current_state
            elif current_state == EMAIL and "@" not in text:
                await update.message.reply_text("❌ لطفاً یک ایمیل معتبر وارد کنید.")
                context.user_data["edit_message"] = await update.message.reply_text(
                    QUESTIONS[current_state], reply_markup=get_keyboard()
                )
                return current_state
            elif current_state == STUDENT_ID and not text.isdigit():
                await update.message.reply_text(
                    "❌ شماره دانشجویی باید فقط شامل اعداد باشد."
                )
                context.user_data["edit_message"] = await update.message.reply_text(
                    QUESTIONS[current_state], reply_markup=get_keyboard()
                )
                return current_state
            elif current_state == ENTRY_YEAR and not text.isdigit():
                await update.message.reply_text("❌ سال ورود باید فقط شامل اعداد باشد.")
                context.user_data["edit_message"] = await update.message.reply_text(
                    QUESTIONS[current_state], reply_markup=get_keyboard()
                )
                return current_state
            elif current_state == DORMITORY and text.lower() not in [
                "بله",
                "خیر",
            ]:
                await update.message.reply_text("❌ لطفاً 'بله' یا 'خیر' را وارد کنید.")
                context.user_data["edit_message"] = await update.message.reply_text(
                    QUESTIONS[current_state], reply_markup=get_keyboard()
                )
                return current_state

            if current_state == DORMITORY:
                context.user_data[field_name] = text.lower() == "بله"
            else:
                context.user_data[field_name] = text

        next_state = current_state + 1
        if next_state > PHOTO:
            return await save_profile(update, context)

        if next_state == ENTRY_YEAR:
            reply_markup = get_entry_year_keyboard()
        elif next_state == DORMITORY:
            reply_markup = get_dormitory_keyboard()
        else:
            reply_markup = get_keyboard()

        context.user_data["edit_message"] = await update.message.reply_text(
            QUESTIONS[next_state], reply_markup=reply_markup
        )
        context.user_data["current_state"] = next_state
        return next_state

    except Exception as e:
        logger.error(f"Error in handle_input: {str(e)}", exc_info=True)
        await update.message.reply_text(
            "❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if "edit_message" in context.user_data:
        await context.user_data["edit_message"].delete()

    if update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        context.user_data["telegram_picture"] = photo_file.file_id

    return await save_profile(update, context)


async def save_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if "user_messages" in context.user_data:
        for message in context.user_data["user_messages"]:
            try:
                await message.delete()
            except:
                pass
        del context.user_data["user_messages"]

    try:
        async with context.db.session() as session:
            profile_id = context.user_data.get("profile_id")
            result = await session.execute(
                select(ProfileModel).where(ProfileModel.id == profile_id)
            )
            profile = result.scalar_one_or_none()

            if not profile:
                raise ValueError("پروفایل یافت نشد.")
            for key, value in context.user_data.items():
                if hasattr(profile, key) and value is not None:
                    setattr(profile, key, value)
            if profile.role == RoleType.STUDENT:
                student_result = await session.execute(
                    select(StudentModel).where(StudentModel.profile_id == profile_id)
                )
                student = student_result.scalar_one_or_none()

                if not student:
                    student = StudentModel(profile_id=profile_id)
                    session.add(student)
                if "student_id" in context.user_data:
                    student.student_id = int(context.user_data["student_id"])
                if "enter_year" in context.user_data:
                    student.enter_year = int(context.user_data["enter_year"])
                if "dormitory" in context.user_data:
                    student.dormitory = context.user_data["dormitory"]

            await session.commit()

    except ValueError as e:
        await update.message.reply_text(
            f"❌ خطا: {str(e)}", reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error saving profile: {str(e)}")
        await update.message.reply_text(
            call_error(),
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END

    success_message = await update.message.reply_text(
        "✅ پروفایل شما با موفقیت بروزرسانی شد.",
        reply_markup=ReplyKeyboardRemove(),
    )
    await asyncio.sleep(1)
    await success_message.delete()
    await bio_handler(update, context)

    return ConversationHandler.END


async def _cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if "user_messages" in context.user_data:
        for message in context.user_data["user_messages"]:
            try:
                await message.delete()
            except:
                pass
        del context.user_data["user_messages"]

    await update.message.reply_text(
        cancel_alert("ویرایش پروفایل"),
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


edit_profile_callback = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_profile_edit, pattern="^edit_profile$")],
    states={
        FIRST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input)],
        LAST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input)],
        PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input)],
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input)],
        STUDENT_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input)],
        ENTRY_YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input)],
        DORMITORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input)],
        PHOTO: [
            MessageHandler(filters.PHOTO, handle_photo),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input),
        ],
    },
    fallbacks=[MessageHandler(filters.Regex("^🚫 انصراف$"), _cancel)],
)
