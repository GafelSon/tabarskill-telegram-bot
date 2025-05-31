# Utils -> channel module

# main lib
import os
from functools import wraps

# dependencies lib
from telegram.ext import ContextTypes, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

# local lib
from app.core.log import channel_warning

# Define the ID
channel = os.getenv("CHANNEL_USERNAME", "@gafelson")
archive = os.getenv("ARCHIVE_USERNAME", "@tabarskill_archive")


async def check_channel_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        chat_member = await context.bot.get_chat_member(
            chat_id=channel, user_id=user.id
        )
        return chat_member.status in ["member", "administrator", "creator"]
    except Exception:
        return False


def require_channel_membership(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        onboarding = (
            f">خطای عدم عضویت در کانال\n"
            f"🌟 دانشجوی محترم، خوش آمدید\! 🌟\n\n"
            f"⚠️ برای دسترسی به تمامی امکانات و خدمات ربات، لطفاً ابتدا در کانال رسمی دانشگاه عضو شوید\.\n\n"
            f"🔥 __پس از عضویت، به راحتی می‌توانید از تمامی قابلیت‌ها و خدمات اختصاصی ربات استفاده کنید\!__\n\n"
            f">تظرتون هستیم و از شما استقبال می‌کنیم\! 🚀\n"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "🎫 عضویت در کانال", url=f"https://t.me/{channel[1:]}"
                )
            ],
            [InlineKeyboardButton("✅ عضو شدم", callback_data="check_membership")],
        ]
        keyboard_layout = InlineKeyboardMarkup(keyboard)

        if not await check_channel_membership(update, context):
            if update.callback_query:
                await update.callback_query.message.reply_text(
                    text=onbording,
                    reply_markup=keyboard_layout,
                    parse_mode="MarkdownV2",
                    disable_web_page_preview=True,
                )
            else:
                await update.message.reply_text(
                    text=onboarding,
                    reply_markup=keyboard_layout,
                    parse_mode="MarkdownV2",
                    disable_web_page_preview=True,
                )
            return ConversationHandler.END
        if isinstance(func, ConversationHandler):
            return func
        return await func(update, context)

    return wrapper


async def check_membership_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if await check_channel_membership(update, context):
        await query.message.edit_text("🎟️ عضویت شما با موفقیت تایید شد!\n")
    else:
        await query.answer(
            channel_warning(),
            show_alert=True,
        )
