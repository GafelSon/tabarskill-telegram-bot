# reminder function

# main lib
# .
# .

# dependencies lib
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select as future_select
from sqlalchemy import select, and_, or_, not_, desc, asc
from telegram.ext import ContextTypes, CallbackContext
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

# local lib
from app.core.logger import logger
from app.database.models.profile import ProfileModel

from ..states import EventState, EventInputHandler

# logger config
logger = logger(__name__)


async def new_event_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    if not query:
        logger.error("SYSTEM:: ReminderHandler:: No callback query found in update")
        return

    async with context.db.session() as session:
        res = await session.execute(
            select(ProfileModel).where(
                ProfileModel.telegram_id == str(query.from_user.id)
            )
        )
        db_user = res.scalar_one_or_none()

        if not db_user:
            await query.answer(...)
            return

        onboarding = (
            f">🎉 **ساخت رویداد جدید** 🎉\n\n\n\n"
            f"🔒 **سطح دسترسی:** عادی\n"
            f"شما می‌توانید یک رویداد جدید برای خودتان ایجاد کنید\.\n\n"
            f"📌 **نوع رویداد:**\n\n"
            f"• 🧑‍💼 رویداد شخصی \(امور مربوط به خود شما\)\n"
            f"• 👥 رویداد گروهی \(در حال توسعه توسط برنامه نویسان\)\n\n\n"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "➕ اضافه کردن رویداد شخصی", callback_data="new_personal_event"
                ),
            ],
        ]

        if db_user.flag:
            onboarding += (
                f">✨ **دسترسی پیشرفته فعال است** ✨\n\n\n"
                f"🔓 این نوع دسترسی مخصوص کاربران سطح بالا می‌باشد — مانند مدیران، برگزارکنندگان یا اعضای منتخب\.\n\n"
                f"📅 شما می‌توانید رویدادهایی با ابعاد بزرگ‌تر ثبت کنید:\n\n"
                f"    • 🏛 رویدادهای رسمی یا دانشگاهی\n"
                f"    • 🎓 نشست‌های علمی، کارگاه‌ها یا همایش‌ها\n"
                f"    • 🤝 برنامه‌های جمعی یا عمومی برای دیگران\n\n"
                f">💡 این رویدادها می‌توانند برای دیگر کاربران قابل مشاهده یا شرکت‌پذیر باشند\. لطفاً با دقت و مسئولیت استفاده نمایید\."
            )
            keyboard.append(
                [
                    InlineKeyboardButton(
                        "🎓 اضافه کردن رویداد دانشگاهی",
                        callback_data="new_university_event",
                    ),
                ]
            )

        keyboard.append(
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="back2reminder"),
            ]
        )

        keyboard_layout = InlineKeyboardMarkup(keyboard)

        await query.answer()
        await query.edit_message_caption(
            caption=onboarding,
            reply_markup=keyboard_layout,
            parse_mode="MarkdownV2",
        )
