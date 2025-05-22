# wallet handler function

# main lib
from decimal import Decimal
from typing import Optional, Tuple

# dependencies lib
from sqlalchemy import select
from telegram.ext import ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Message

# local lib
from app.core.log import start_warning, internal_error
from app.core.logger import logger
from app.core.decor import message_object, effectiveUser
from app.utils.escape import markdownES as mds
from app.database.models import ProfileModel, WalletBase

# config logger
logger = logger(__name__)


@message_object
@effectiveUser
async def handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE, message: Message = None
) -> None:
    user = update.effective_user

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
            await message.reply_text(start_warning())
            return

        token_amount = 0
        if wallet and wallet.token is not None:
            if isinstance(wallet.token, Decimal):
                token_amount = float(wallet.token)
            else:
                token_amount = wallet.token

        formatted_token = (
            f"{token_amount:.2f}" if isinstance(token_amount, float) else token_amount
        )

        onboarding = (
            f">کیف پول\n\n\n"
            f"*نام کاربری:* \\@{mds(db_user.telegram_username or 'کاربر جدید')}\n\n"
            f"💰 *موجودی کیف پول شما*:\n\n"
            f"🪙 *اعتبار باقیمانده:* {mds(formatted_token)} قرون\n\n"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "🕹️ آموزش استفاده از ربات", callback_data="show_tutorial"
                )
            ],
            [InlineKeyboardButton("💰 شارژ کیف پول", callback_data="show_get_token")],
        ]
        keyboard_layout = InlineKeyboardMarkup(keyboard)

        await message.reply_photo(
            photo="AgACAgQAAyEGAASLt5ydAAMmZ_yo0BP-GMN8Vjv7pn9FojWPr4IAAnDGMRstPuFT2ygGVy3kLJ8BAAMCAANtAAM2BA",
            caption=onboarding,
            reply_markup=keyboard_layout,
            parse_mode="MarkdownV2",
        )
