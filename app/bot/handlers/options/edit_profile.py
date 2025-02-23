from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from sqlalchemy import select
from app.database.models import User
import logging

logger = logging.getLogger(__name__)

# Handle conversation fuilds
(
    FIRST_NAME,
    LAST_NAME,
    PHONE,
    UNIVERSITY_ID,
    FACULTY,
    MAJOR,
    ENTRY_YEAR,
    PHOTO,
) = range(8)

def get_keyboard():
    return ReplyKeyboardMarkup([
        ["قبلی ◀️","▶️ بعدی"],
        ["🚫 انصراف"]
    ], resize_keyboard=True)

QUESTIONS = {
    FIRST_NAME: "👤 لطفاً نام خود را وارد کنید:",
    LAST_NAME: "👥 لطفاً نام خانوادگی خود را وارد کنید:",
    PHONE: "📱 لطفاً شماره تماس خود را وارد کنید:",
    UNIVERSITY_ID: "🎓 لطفاً شماره دانشجویی خود را وارد کنید:",
    FACULTY: "🏛️ لطفاً نام دانشکده خود را وارد کنید:",
    MAJOR: "📚 لطفاً رشته تحصیلی خود را وارد کنید:",
    ENTRY_YEAR: "📅 لطفاً سال ورود خود را وارد کنید:",
    PHOTO: "🖼️ لطفاً عکس پروفایل خود را ارسال کنید:",
}

FIELDS = {
    FIRST_NAME: 'first_name',
    LAST_NAME: 'last_name',
    PHONE: 'phone',
    UNIVERSITY_ID: 'university_id',
    FACULTY: 'faculty',
    MAJOR: 'major',
    ENTRY_YEAR: 'entry_year',
    PHOTO: 'profile',
}

async def start_profile_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the profile editing process."""
    await update.callback_query.answer()
    context.user_data['edit_message'] = await update.callback_query.message.reply_text(
        QUESTIONS[FIRST_NAME],
        reply_markup=get_keyboard()
    )
    context.user_data['current_state'] = FIRST_NAME
    return FIRST_NAME

FACULTIES = [
    "دانشکده امام محمد باقر (ع) ساری شماره۱",
    "دانشکده امام محمد باقر (ع) ساری شماره۲",
    "دانشکده قدسیه دختران ساری",
    "دانشکده های دیگر استان"
]

MAJORS = {
    "دانشکده امام محمد باقر (ع) ساری شماره۱": ["کامپیوتر", "برق", "تاسیسات", "معماری", "عمران"],
    "دانشکده امام محمد باقر (ع) ساری شماره۲": ["کامپیوتر", "برق", "تاسیسات", "معماری", "عمران"],
    "دانشکده دختران ساری": ["کامپیوتر", "برق", "تاسیسات", "معماری", "عمران"],
    "دانشکده های دیگر استان": ["کامپیوتر", "برق", "تاسیسات", "معماری", "عمران"],
}

ENTRY_YEARS = [str(year) for year in range(1400, 1405)]

def get_selection_keyboard(options, columns=2):
    keyboard = [options[i:i + columns] for i in range(0, len(options), columns)]
    keyboard.append(["قبلی ◀️", "▶️ بعدی"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if 'user_messages' not in context.user_data:
        # Save user message while edit profile
        context.user_data['user_messages'] = []
    context.user_data['user_messages'].append(update.message)

    current_state = context.user_data.get('current_state', FIRST_NAME)
    text = update.message.text

    if 'edit_message' in context.user_data:
        await context.user_data['edit_message'].delete()

    if text == "قبلی ◀️":
        if current_state == FIRST_NAME:
            return await cancel(update, context)
        if current_state > FIRST_NAME:
            next_state = current_state - 1
            reply_markup = get_keyboard()
            # Special handling for selection fields
            if next_state == FACULTY:
                reply_markup = get_selection_keyboard(FACULTIES)
            elif next_state == MAJOR and 'faculty' in context.user_data:
                faculty = context.user_data['faculty']
                reply_markup = get_selection_keyboard(MAJORS.get(faculty, []))
            elif next_state == ENTRY_YEAR:
                reply_markup = get_selection_keyboard(ENTRY_YEARS, columns=3)
            
            context.user_data['edit_message'] = await update.message.reply_text(
                QUESTIONS[next_state],
                reply_markup=reply_markup
            )
            context.user_data['current_state'] = next_state
            return next_state
        return current_state

    if text == "▶️ بعدی":
        next_state = current_state + 1
    elif text == "🚫 انصراف":
        return await cancel(update, context)
    else:
        if text != "▶️ بعدی":
            field_name = FIELDS[current_state]
            context.user_data[field_name] = text
        next_state = current_state + 1

    # Check if we're done
    if next_state > PHOTO:
        return await save_profile(update, context)

    reply_markup = get_keyboard()

    if next_state == FACULTY:
        reply_markup = get_selection_keyboard(FACULTIES)
    elif next_state == MAJOR:
        faculty = context.user_data.get('faculty')
        majors = MAJORS.get(faculty, [])
        reply_markup = get_selection_keyboard(majors)
    elif next_state == ENTRY_YEAR:
        reply_markup = get_selection_keyboard(ENTRY_YEARS, columns=3)

    context.user_data['edit_message'] = await update.message.reply_text(
        QUESTIONS[next_state],
        reply_markup=reply_markup
    )
    context.user_data['current_state'] = next_state
    return next_state

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if 'edit_message' in context.user_data:
        await context.user_data['edit_message'].delete()

    if update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        context.user_data['profile'] = photo_file.file_id
    
    return await save_profile(update, context)

async def save_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Delete user messages
    if 'user_messages' in context.user_data:
        for message in context.user_data['user_messages']:
            try:
                await message.delete()
            except:
                pass
        del context.user_data['user_messages']

    async with context.db.session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == update.effective_user.id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            for key, value in context.user_data.items():
                if value is not None and key in FIELDS.values():
                    setattr(user, key, value)
            await session.commit()

    await update.message.reply_text(
        "🎊 دانشجوی گرامی پروفایل شما بروزرسانی گردید.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Delete user messages
    if 'user_messages' in context.user_data:
        for message in context.user_data['user_messages']:
            try:
                await message.delete()
            except:
                pass
        del context.user_data['user_messages']

    await update.message.reply_text(
        "❌ ویرایش پروفایل توسط شما لغو گردید.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

edit_profile_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_profile_edit, pattern="^edit_profile$")],
    states={
        FIRST_NAME: [MessageHandler(filters.TEXT, handle_input)],
        LAST_NAME: [MessageHandler(filters.TEXT, handle_input)],
        PHONE: [MessageHandler(filters.TEXT, handle_input)],
        UNIVERSITY_ID: [MessageHandler(filters.TEXT, handle_input)],
        FACULTY: [MessageHandler(filters.TEXT, handle_input)],
        MAJOR: [MessageHandler(filters.TEXT, handle_input)],
        ENTRY_YEAR: [MessageHandler(filters.TEXT, handle_input)],
        PHOTO: [
            MessageHandler(filters.PHOTO, handle_photo),
            MessageHandler(filters.TEXT, handle_input)
        ],
    },
    fallbacks=[MessageHandler(filters.TEXT & filters.Regex("^انصراف$"), cancel)],
)