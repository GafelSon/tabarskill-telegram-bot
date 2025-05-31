# Utils -> tokens module

# main lib
# .
# .

# dependencies lib
from sqlalchemy import select
from decimal import Decimal
from telegram.ext import ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

# local lib
from app.core.logger import logger
from app.core.log import start_warning
from app.utils.escape import markdownES as mds
from app.database.models import ProfileModel, WalletBase

# logger config
logger = logger(__name__)


def check_tokens(cost: float = 0.75):
    def decorator(func):
        async def wrapper(
            update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
        ):
            user = update.effective_user
            if user is None:
                logger.error("SYSTEM:: No effective user in the update")
                return

            async with context.db.session() as session:
                result = await session.execute(
                    select(ProfileModel, WalletBase)
                    .join(WalletBase, ProfileModel.id == WalletBase.profile_id)
                    .where(ProfileModel.telegram_id == user.id)
                )
                row = result.first()

                if not row:
                    await update.message.reply_text(start_warning())
                    return

                db_user, wallet = row

                if wallet.token < cost:
                    keyboard = [
                        [
                            InlineKeyboardButton(
                                "💳 افزایش اعتبار", callback_data="/wallet"
                            )
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text(
                        f">موجودی ناکافی\!\n\n\n"
                        f"🔔 دانجشوی عزیز، برای استفاده از این امکان، اعتبار کافی ندارید\.\n\n"
                        f"    💰 *اعتبار مورد نیاز:* {mds(str(cost))} *قرون*\n"
                        f"    👛 *موجودی شما:* {mds(str(wallet.token))} *قرون*\n\n"
                        f"➕ میتوانید با دستور /wallet اطلاعات کیف پول خود را مشاهده کنید\.\n\n"
                        f"> 💸 در این سرویس، پس از هر استفاده، هزینه از کیف پول شما کسر می‌شود\. برای افزایش اعتبار، روی دکمه زیر کلیک کنید:",
                        parse_mode="MarkdownV2",
                        reply_markup=reply_markup,
                    )
                    return

                wallet.token -= Decimal(str(cost))
                await session.commit()
                return await func(update, context, *args, **kwargs)

        return wrapper

    return decorator
