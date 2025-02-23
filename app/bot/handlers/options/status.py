from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
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
from uuid import uuid4

logger = logging.getLogger(__name__)

(
    SHOW_STATUS,
    PREMIUM_OPTIONS,
    FREE_TOKEN,
    INVITE_FRIENDS,
) = range(4)

ADMIN_ID = "5455523252"
ADMIN_USERNAME = "tabarskill"

def get_status_text(db_user):
    return (
f"""
💫 *وضعیت اشتراک شما در تبرسکیل‌بات*

👤 *کاربر:* {db_user.first_name or '—'} {db_user.last_name or '—'}
🆔 *نام کاربری:* @{db_user.username or '—'}

💎 *نوع اشتراک:* {'✨ ویژه' if db_user.is_premium else '🔹 رایگان'}
🎫 *توکن‌های باقیمانده:* {db_user.tokens or 0} عدد
📅 *تاریخ عضویت:* {db_user.created_at.strftime('%y/%m/%d %H:%M')}

{'✨ شما دسترسی ویژه دارید و می‌توانید از تمام امکانات ربات استفاده کنید.' if db_user.is_premium else '⭐️ برای استفاده از امکانات ویژه، اشتراک تهیه کنید.'}
"""
    )

async def start_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the status viewing process."""
    await update.callback_query.answer()
    
    async with context.db.session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == update.effective_user.id)
        )
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            await update.callback_query.message.reply_text(
                "❌ لطفا ابتدا با دستور /start ثبت‌نام کنید."
            )
            return ConversationHandler.END

    if db_user.is_premium:
        keyboard = [
            [
                InlineKeyboardButton("✨ درخواست تمدید اشتراک", callback_data="request_premium"),
                InlineKeyboardButton("📢 دعوت دوستان", callback_data="invite_friends")
            ],
            [InlineKeyboardButton("انصراف", callback_data="cancel")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("✨ درخواست اشتراک ویژه", callback_data="request_premium")],
            [InlineKeyboardButton("🎁 دریافت اعتبار رایگان", callback_data="free_token")],
            [InlineKeyboardButton("انصراف", callback_data="cancel")]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.user_data['status_message'] = await update.callback_query.message.reply_text(
        get_status_text(db_user),
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return SHOW_STATUS

async def handle_status_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == "request_premium":
        await query.message.edit_text(
            f"💫 برای {'تمدید' if query.message.reply_markup.inline_keyboard[0][0].text.startswith('✨ درخواست تمدید') else 'خرید'} اشتراک ویژه، لطفاً با ادمین در ارتباط باشید:\n"
            f"👤 @{ADMIN_USERNAME}"
        )
        return ConversationHandler.END
    
    elif query.data == "cancel":
        if 'status_message' in context.user_data:
            await context.user_data['status_message'].delete()
        await query.message.edit_text("❌ نمایش وضعیت لغو شد.")
        return ConversationHandler.END
    
    return SHOW_STATUS

status_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_status, pattern="^show_status$")],
    states={
        SHOW_STATUS: [CallbackQueryHandler(handle_status_choice)],
        FREE_TOKEN: [CallbackQueryHandler(handle_status_choice)],
        INVITE_FRIENDS: [CallbackQueryHandler(handle_status_choice)],
    },
    fallbacks=[CallbackQueryHandler(handle_status_choice, pattern="^cancel$")],
)
