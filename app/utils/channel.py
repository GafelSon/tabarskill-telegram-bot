from functools import wraps
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

CHANNEL_USERNAME = "@gafblog"

async def check_channel_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        chat_member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user.id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

def require_channel_membership(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = (
            "🌟 دانشجوی عزیز 🌟\n\n"
            "⚠️ برای استفاده از امکانات ربات، لطفاً ابتدا در کانال ما عضو شوید:\n"
            "🔥 پس از عضویت، میتوانید از تمامی امکانات ربات استفاده کنید!"
        )

        keyboard = [
            [InlineKeyboardButton("🔰 عضویت در کانال 🔰", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton("✅ عضو شدم", callback_data="check_membership")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if not await check_channel_membership(update, context):
            await update.message.reply_text(
                text=message,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
            return
        return await func(update, context)
    return wrapper

async def check_membership_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if await check_channel_membership(update, context):
        await query.message.edit_text(
            "✅ عضویت شما با موفقیت تایید شد!\n"
            "اکنون می‌توانید از امکانات ربات استفاده کنید. 🌟"
        )
    else:
        await query.answer(
            "❌ هنوز عضو کانال نشده‌اید!\n"
            "لطفاً ابتدا در کانال عضو شوید.",
            show_alert=True
        )