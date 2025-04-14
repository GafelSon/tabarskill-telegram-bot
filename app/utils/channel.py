# app.utils.channel.py
import os
from functools import wraps

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

# Define the channel username
channel = os.getenv("CHANNEL_USERNAME", "@gafelson")
archive = os.getenv("ARCHIVE_USERNAME", "@tabarskill_archive")


# Define the channel membership check function
async def check_channel_membership(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    try:
        user = update.effective_user
        chat_member = await context.bot.get_chat_member(
            chat_id=channel, user_id=user.id
        )
        return chat_member.status in ["member", "administrator", "creator"]
    except Exception:
        return False


# Define the channel membership required decorator
def require_channel_membership(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = (
            ">خطای عدم عضویت در کانال\n"
            "🌟 دانشجوی محترم، خوش آمدید\! 🌟\n\n"
            "⚠️ برای دسترسی به تمامی امکانات و خدمات ربات، لطفاً ابتدا در کانال رسمی دانشگاه عضو شوید\.\n\n"
            "🔥 __پس از عضویت، به راحتی می‌توانید از تمامی قابلیت‌ها و خدمات اختصاصی ربات استفاده کنید\!__\n\n"
            ">تظرتون هستیم و از شما استقبال می‌کنیم\! 🚀\n"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "🎫 عضویت در کانال", url=f"https://t.me/{channel[1:]}"
                )
            ],
            [
                InlineKeyboardButton(
                    "✅ عضو شدم", callback_data="check_membership"
                )
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if not await check_channel_membership(update, context):
            await update.message.reply_text(
                text=message,
                reply_markup=reply_markup,
                parse_mode="MarkdownV2",
                disable_web_page_preview=True,
            )
            return
        return await func(update, context)

    return wrapper


# Define the channel membership check callback
async def check_membership_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    if await check_channel_membership(update, context):
        await query.message.edit_text("🎟️ عضویت شما با موفقیت تایید شد!\n")
    else:
        await query.answer(
            "🪃 هنوز عضو کانال نشده‌اید!\n" "لطفاً ابتدا در کانال عضو شوید.",
            show_alert=True,
        )
