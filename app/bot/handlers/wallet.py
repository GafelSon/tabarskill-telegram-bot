# app.bot.handlers.tokens.py
import logging
from decimal import Decimal
from typing import Optional, Tuple

from sqlalchemy import select
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.database.models import ProfileModel, WalletBase

logger = logging.getLogger(__name__)


def escape_markdown(text: str) -> str:
    """Escape special characters for MarkdownV2 format."""
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
        "@",
    ]
    for char in special_chars:
        text = str(text).replace(char, "\\" + char)
    return text


async def wallet_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle wallet and token information display for users."""
    user = update.effective_user
    if user is None:
        logger.error("SYSTEM: No effective user in the update")
        return

    # Get the user from the database
    async with context.db.session() as session:
        result = await session.execute(
            select(ProfileModel, WalletBase)
            .join(
                WalletBase,
                ProfileModel.id == WalletBase.profile_id,
                isouter=True,
            )
            .where(ProfileModel.telegram_id == user.id)
        )
        db_user_wallet: Optional[Tuple[ProfileModel, Optional[WalletBase]]] = (
            result.first()
        )
        db_user, wallet = db_user_wallet or (None, None)

        if not db_user:
            await update.message.reply_text(
                "❌ شما هنوز ثبت‌نام نکرده‌اید. لطفا ابتدا از دستور /start استفاده کنید!"
            )
            return

        # Get token amount, handling different data types
        token_amount = 0
        if wallet and wallet.token is not None:
            if isinstance(wallet.token, Decimal):
                token_amount = float(wallet.token)
            else:
                token_amount = wallet.token

        # Format token amount with proper decimal places
        formatted_token = (
            f"{token_amount:.2f}"
            if isinstance(token_amount, float)
            else token_amount
        )

        tokens_message = (
            f">کیف پول\n\n\n"
            f"💰 *موجودی کیف پول شما*:\n\n"
            f"*نام کاربری:* \\@{escape_markdown(db_user.telegram_username or 'کاربر جدید')}\n\n"
            f"🪙 *اعتبار باقیمانده:* {escape_markdown(formatted_token)} قرون\n\n"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "🕹️ آموزش استفاده از ربات", callback_data="tutorial"
                )
            ],
            [
                InlineKeyboardButton(
                    "💰 شارژ کیف پول", callback_data="buy_premium"
                )
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_photo(
            photo="AgACAgQAAyEGAASLt5ydAAMmZ_yo0BP-GMN8Vjv7pn9FojWPr4IAAnDGMRstPuFT2ygGVy3kLJ8BAAMCAANtAAM2BA",
            caption=tokens_message,
            reply_markup=reply_markup,
            parse_mode="MarkdownV2",
        )
