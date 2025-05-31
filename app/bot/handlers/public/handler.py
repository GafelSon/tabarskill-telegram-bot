# public handler

# main lib
from datetime import datetime

# dependencies lib
from sqlalchemy import select
from telegram.ext import ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

# local lib
from app.core.decor import effectiveUser
from app.core.log import internal_error, start_warning, cancel_alert
from app.core.logger import logger
from app.utils.escape import markdownES as mds
from app.database.models import ProfileModel

# logger config
logger = logger(__name__)


@effectiveUser
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    try:
        async with context.db.session() as session:
            res = await session.execute(
                select(ProfileModel).where(ProfileModel.telegram_id == str(user.id))
            )
            db_user = res.scalar_one_or_none()

            if not db_user:
                await update.message.reply_text(start_warning())
                return

            if not db_user.support and not db_user.flag:
                await update.message.reply_text(
                    "❌ شما مجوز ارسال پیام عمومی ندارید.\n"
                    "برای دریافت مجوز با پشتیبانی تماس بگیرید."
                )
                return

            welcome_message = (
                f"📢 *پنل ارسال پیام عمومی*\n\n"
                f"👋 سلام {mds(user.first_name)} عزیز\!\n\n"
                f"🎯 *راهنمای استفاده:*\n"
                f"    📝 پیام، عکس یا ویدیوی خود را ارسال کنید\n"
                f"    👁️ پیش‌نمایش پیام را بررسی کنید\n"
                f"    ✅ پیام را برای همه کاربران ارسال کنید\n\n"
                f"⚠️ *نکات مهم:*\n"
                f"    • پیام باید مناسب و مفید باشد\n"
                f"    • از ارسال اسپم خودداری کنید\n"
                f"    • پیام‌های نامناسب منجر به مسدود شدن می‌شود\n\n"
                f"🚀 *اکنون پیام خود را ارسال کنید\.\.\.*"
            )

            keyboard = [
                [InlineKeyboardButton("❌ انصراف", callback_data="cancel_public")],
                [InlineKeyboardButton("📚 راهنمای کامل", callback_data="show_help")],
            ]
            keyboard_layout = InlineKeyboardMarkup(keyboard)

            context.user_data["public_step"] = "waiting_message"
            context.user_data["public_user_id"] = user.id
            sent_welcome = await update.message.reply_text(
                welcome_message, parse_mode="MarkdownV2", reply_markup=keyboard_layout
            )
            context.user_data["public_welcome_message_id"] = sent_welcome.message_id
            logger.info(
                f"SYSTEM:: PublicHandler:: {user.id}-{user.username} started public message"
            )

    except Exception as e:
        logger.error(
            f"SYSTEM:: PublicHandler:: Error in public handler: {e}", exc_info=True
        )
        await update.message.reply_text(internal_error())


async def handle_public_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    user = update.effective_user
    if context.user_data.get("public_step") != "waiting_message":
        return

    if context.user_data.get("public_user_id") != user.id:
        return

    try:
        context.user_data["public_message"] = update.message
        context.user_data["public_step"] = "preview"

        preview_text = f""

        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ ارسال برای همه", callback_data="confirm_broadcast"
                )
            ],
            [InlineKeyboardButton("❌ لغو", callback_data="cancel_public")],
        ]
        keyboard_layout = InlineKeyboardMarkup(keyboard)

        sent = None
        if update.message.photo:
            sent = await update.message.reply_photo(
                photo=update.message.photo[-1].file_id,
                caption=f"{preview_text}{mds(update.message.caption or '')}",
                parse_mode="MarkdownV2",
                reply_markup=keyboard_layout,
            )
        elif update.message.video:
            sent = await update.message.reply_video(
                video=update.message.video.file_id,
                caption=f"{preview_text}{mds(update.message.caption or '')}",
                parse_mode="MarkdownV2",
                reply_markup=keyboard_layout,
            )
        elif update.message.document:
            sent = await update.message.reply_document(
                document=update.message.document.file_id,
                caption=f"{preview_text}{mds(update.message.caption or '')}",
                parse_mode="MarkdownV2",
                reply_markup=keyboard_layout,
            )
        else:
            preview_message = f"{preview_text}{mds(update.message.text or '')}"
            sent = await update.message.reply_text(
                preview_message, parse_mode="MarkdownV2", reply_markup=keyboard_layout
            )

        if sent:
            context.user_data["public_preview_message_id"] = sent.message_id
        welcome_message_id = context.user_data.get("public_welcome_message_id")
        if welcome_message_id:
            try:
                await context.bot.delete_message(
                    chat_id=user.id, message_id=welcome_message_id
                )
            except Exception as del_err:
                logger.warning(f"Could not delete public welcome message: {del_err}")

        logger.info(f"SYSTEM:: PublicHandler:: {user.id} created message preview")

    except Exception as e:
        logger.error(
            f"SYSTEM:: PublicHandler:: Error in message preview: {e}", exc_info=True
        )
        await update.message.reply_text("❌ خطا در ایجاد پیش‌نمایش پیام.")


async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    try:
        stored_message = context.user_data.get("public_message")
        if not stored_message:
            await update.callback_query.answer("❌ پیامی برای ارسال یافت نشد!")
            return

        async with context.db.session() as session:
            result = await session.execute(select(ProfileModel))
            all_users = result.scalars().all()
            db_user_result = await session.execute(
                select(ProfileModel).where(ProfileModel.telegram_id == str(user.id))
            )
            db_user = db_user_result.scalar_one_or_none()

            success_count = 0
            fail_count = 0
            preview_message_id = context.user_data.get("public_preview_message_id")
            if preview_message_id:
                try:
                    await context.bot.delete_message(
                        chat_id=user.id, message_id=preview_message_id
                    )
                except Exception as del_err:
                    logger.warning(f"Could not delete preview message: {del_err}")

            status_message = await context.bot.send_message(
                chat_id=user.id,
                text=f"🚀 *شروع ارسال پیام\.\.\.*\n\n"
                f"📊 در حال ارسال برای {len(all_users)} کاربر\.\.\.",
                parse_mode="MarkdownV2",
            )
            if db_user and hasattr(db_user, "flag") and db_user.flag:
                faculty_name = db_user.faculty_name
                all_users = [
                    profile
                    for profile in all_users
                    if profile.faculty_name == faculty_name
                ]

            for profile in all_users:
                try:
                    telegram_id = int(profile.telegram_id)
                    if telegram_id == user.id:
                        continue

                    broadcast_prefix = f">📢 *اطلاعیه عمومی*\n\n"

                    if stored_message.photo:
                        await context.bot.send_photo(
                            chat_id=telegram_id,
                            photo=stored_message.photo[-1].file_id,
                            caption=f"{broadcast_prefix}{mds(stored_message.caption or '')}",
                            parse_mode="MarkdownV2",
                        )
                    elif stored_message.video:
                        await context.bot.send_video(
                            chat_id=telegram_id,
                            video=stored_message.video.file_id,
                            caption=f"{broadcast_prefix}{mds(stored_message.caption or '')}",
                            parse_mode="MarkdownV2",
                        )
                    elif stored_message.document:
                        await context.bot.send_document(
                            chat_id=telegram_id,
                            document=stored_message.document.file_id,
                            caption=f"{broadcast_prefix}{mds(stored_message.caption or '')}",
                            parse_mode="MarkdownV2",
                        )
                    else:
                        broadcast_text = (
                            f"{broadcast_prefix}{mds(stored_message.text or '')}"
                        )
                        await context.bot.send_message(
                            chat_id=telegram_id,
                            text=broadcast_text,
                            parse_mode="MarkdownV2",
                        )

                    success_count += 1

                except Exception as send_error:
                    fail_count += 1
                    logger.warning(
                        f"Failed to send to user {profile.telegram_id}: {send_error}"
                    )
            report_message = (
                f"✅ *گزارش ارسال پیام عمومی*\n\n"
                f"📊 *آمار:*\n"
                f"    ✅ ارسال موفق: {success_count}\n"
                f"    ❌ ارسال ناموفق: {fail_count}\n"
                f"    📱 کل کاربران: {len(all_users)}\n\n"
                f"🎉 پیام شما با موفقیت برای همه کاربران ارسال شد\!"
            )

            await context.bot.send_message(
                chat_id=user.id, text=report_message, parse_mode="MarkdownV2"
            )

            try:
                if status_message:
                    await context.bot.delete_message(
                        chat_id=user.id, message_id=status_message.message_id
                    )
            except Exception as del_err:
                logger.warning(f"Could not delete broadcast status message: {del_err}")

            # Clear user data
            context.user_data.clear()

            logger.info(
                f"SYSTEM:: PublicHandler:: {user.id} broadcasted message to {success_count} users"
            )

    except Exception as e:
        logger.error(f"SYSTEM:: PublicHandler:: Error in broadcast: {e}", exc_info=True)
        await update.callback_query.answer("❌ خطا در ارسال پیام عمومی!")


async def _cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    welcome_message_id = context.user_data.get("public_welcome_message_id")
    if welcome_message_id:
        try:
            await context.bot.delete_message(
                chat_id=user.id, message_id=welcome_message_id
            )
        except Exception as del_err:
            logger.warning(f"Could not delete public welcome message: {del_err}")
    preview_message_id = context.user_data.get("public_preview_message_id")
    if preview_message_id:
        try:
            await context.bot.delete_message(
                chat_id=user.id, message_id=preview_message_id
            )
        except Exception as del_err:
            logger.warning(f"Could not delete public preview message: {del_err}")
    status_message_id = context.user_data.get("public_status_message_id")
    if status_message_id:
        try:
            await context.bot.delete_message(
                chat_id=user.id, message_id=status_message_id
            )
        except Exception as del_err:
            logger.warning(f"Could not delete broadcast status message: {del_err}")
    context.user_data.clear()
    await update.effective_message.reply_text(cancel_alert("ارسال پیام عمومی"))
