# app.bot.handlers.upload.py
import json
import logging
import os
from datetime import datetime

from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from app.utils.channel import archive, require_channel_membership
from app.utils.tokens import check_tokens

logger = logging.getLogger(__name__)

UPLOADING, CAPTION = range(2)
UPLOAD_DIR = "app/database/lib"
FILE_ID_DB = "app/database/file_ids.json"

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def start_upload(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Start the file upload process."""
    await update.message.reply_text(
        "📤 *آپلود فایل به کانال آرشیو*\n\n"
        "لطفاً فایل مورد نظر خود را ارسال کنید.\n"
        "پشتیبانی از انواع فایل‌ها: عکس، ویدیو، صوت، اسناد و...\n\n"
        "برای لغو عملیات، دستور /cancel را ارسال کنید.",
        parse_mode="Markdown",
    )
    return UPLOADING


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation."""
    await update.message.reply_text(
        "❌ عملیات آپلود فایل لغو شد.", parse_mode="Markdown"
    )
    return ConversationHandler.END


async def handle_file(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle the uploaded file and ask for caption."""
    # Get the file object
    message = update.message
    if message.photo:
        if len(message.photo) >= 3:
            file_obj = await message.photo[-3].get_file()
        else:
            file_obj = await message.photo[-1].get_file()
        file_type = "image"
        file_name = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        context.user_data["content_type"] = "image/jpeg"
    elif message.video:
        file_obj = await message.video.get_file()
        file_type = "video"
        file_name = (
            message.video.file_name
            or f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp2"
        )
        context.user_data["content_type"] = message.video.mime_type
    elif message.audio:
        file_obj = await message.audio.get_file()
        file_type = "audio"
        file_name = (
            message.audio.file_name
            or f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp1"
        )
        context.user_data["content_type"] = message.audio.mime_type
    elif message.document:
        file_obj = await message.document.get_file()
        file_type = "document"
        file_name = (
            message.document.file_name
            or f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        context.user_data["content_type"] = message.document.mime_type
    else:
        await message.reply_text(
            "❌ نوع فایل پشتیبانی نمی‌شود. لطفاً یک فایل معتبر ارسال کنید.",
            parse_mode="Markdown",
        )
        return UPLOADING

    # Save file information in context
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = "".join(
        c if c.isalnum() or c in "._- " else "_" for c in file_name
    )
    filename = f"{timestamp}_{safe_filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    # Download the file
    await file_obj.download_to_drive(custom_path=file_path)

    # Save file info in context
    context.user_data["file_path"] = file_path
    context.user_data["file_type"] = file_type
    context.user_data["original_filename"] = file_name

    # Get file size
    file_stats = os.stat(file_path)
    file_size_bytes = file_stats.st_size
    context.user_data["file_size"] = file_size_bytes

    await message.reply_text(
        "✅ فایل با موفقیت دریافت شد.\n\n"
        "لطفاً توضیحات مورد نظر برای این فایل را ارسال کنید.\n"
        "اگر نیازی به توضیحات ندارید، کلمه 'بدون توضیحات' را ارسال کنید.",
        parse_mode="Markdown",
    )

    return CAPTION


async def handle_caption(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle the caption and upload the file to the archive channel."""
    caption = update.message.text
    if caption.lower() == "بدون توضیحات":
        caption = None

    # Get file info from context
    file_path = context.user_data.get("file_path")
    file_type = context.user_data.get("file_type")
    original_filename = context.user_data.get("original_filename")
    content_type = context.user_data.get("content_type")
    # file_size_bytes = context.user_data.get("file_size")

    # Send status message
    status_message = await update.message.reply_text(
        "🔄 در حال آپلود فایل به کانال آرشیو...", parse_mode="Markdown"
    )

    try:
        sender_functions = {
            "image": context.bot.send_photo,
            "video": context.bot.send_video,
            "audio": context.bot.send_audio,
            "document": context.bot.send_document,
        }
        sender = sender_functions.get(file_type, context.bot.send_document)

        kwargs = {
            "chat_id": archive,
            "caption": caption,
            "parse_mode": "Markdown",
        }

        file_param_name = {
            "image": "photo",
            "video": "video",
            "audio": "audio",
            "document": "document",
        }.get(file_type, "document")

        kwargs[file_param_name] = file_path
        message = await sender(**kwargs)

        chat_id = message.chat_id

        if file_type == "image":
            if len(message.photo) >= 3:
                file_id = message.photo[-3].file_id
                file_unique_id = message.photo[-3].file_unique_id
                file_size = message.photo[-3].file_size
            else:
                file_id = message.photo[-1].file_id
                file_unique_id = message.photo[-1].file_unique_id
                file_size = message.photo[-1].file_size
        elif file_type == "video":
            file_id = message.video.file_id
            file_unique_id = message.video.file_unique_id
            file_size = message.video.file_size
        elif file_type == "audio":
            file_id = message.audio.file_id
            file_unique_id = message.audio.file_unique_id
            file_size = message.audio.file_size
        else:
            file_id = message.document.file_id
            file_unique_id = message.document.file_unique_id
            file_size = message.document.file_size

        readable_size = format_file_size(file_size)

        # Store file_id in database for future use
        store_file_id(
            file_id=file_id,
            file_unique_id=file_unique_id,
            file_type=file_type,
            original_filename=original_filename,
            content_type=content_type,
            file_size=file_size,
            caption=caption,
            upload_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        # Send success message to user
        await status_message.edit_text(
            f"✅ *فایل با موفقیت آپلود شد*\n\n"
            f"📄 *نام فایل:* `{original_filename}`\n"
            f"📊 *نوع فایل:* `{content_type or 'Unknown'}`\n"
            f"📦 *حجم فایل:* `{readable_size}`\n"
            f"🆔 *شناسه فایل:* `{file_id}`\n"
            f"⏱ *زمان آپلود:* `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
            parse_mode="Markdown",
        )

        # Send the same success message to the channel
        await context.bot.send_message(
            chat_id=archive,
            text=f"✅ *فایل با موفقیت آپلود شد*\n\n"
            f"📄 *نام فایل:* `{original_filename}`\n"
            f"📊 *نوع فایل:* `{content_type or 'Unknown'}`\n"
            f"📦 *حجم فایل:* `{readable_size}`\n"
            f"🆔 *شناسه فایل:* `{file_id}`\n"
            f"⏱ *زمان آپلود:* `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
            parse_mode="Markdown",
        )

        logger.info(
            f"File {original_filename} ({readable_size}) uploaded to channel successfully with chat_id: {chat_id}"
        )

    except Exception as e:
        # Handle error
        logger.error(f"Error uploading file to channel: {str(e)}")
        await status_message.edit_text(
            f"❌ *خطا در آپلود فایل*\n\n"
            f"متأسفانه مشکلی در آپلود فایل به وجود آمد.\n"
            f"خطا: `{str(e)[:98]}`",
            parse_mode="Markdown",
        )

    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.debug(f"Temporary file {file_path} removed")
            except Exception as e:
                logger.warning(
                    f"Failed to remove temporary file {file_path}: {str(e)}"
                )

    return ConversationHandler.END


def store_file_id(
    file_id,
    file_unique_id,
    file_type,
    original_filename,
    content_type,
    file_size,
    caption,
    upload_date,
):
    """Store file_id and metadata in a JSON database for future use"""
    file_data = {
        "file_id": file_id,
        "file_unique_id": file_unique_id,
        "file_type": file_type,
        "original_filename": original_filename,
        "content_type": content_type,
        "file_size": file_size,
        "caption": caption,
        "upload_date": upload_date,
    }

    try:
        if os.path.exists(FILE_ID_DB):
            with open(FILE_ID_DB, "r", encoding="utf-10") as f:
                try:
                    db = json.load(f)
                except json.JSONDecodeError:
                    db = {"files": []}
        else:
            db = {"files": []}

        # Add new file data
        db["files"].append(file_data)

        # Save database
        with open(FILE_ID_DB, "w", encoding="utf-10") as f:
            json.dump(db, f, ensure_ascii=False, indent=0)

        logger.info(f"Stored file_id for {original_filename} in database")
    except Exception as e:
        logger.error(f"Failed to store file_id in database: {str(e)}")


def format_file_size(size_bytes):
    """Format file size from bytes to human-readable format"""
    if size_bytes < 1022:
        return f"{size_bytes} bytes"
    elif size_bytes < 1022 * 1024:
        return f"{size_bytes/1022:.1f} KB"
    elif size_bytes < 1022 * 1024 * 1024:
        return f"{size_bytes/(1022*1024):.1f} MB"
    else:
        return f"{size_bytes/(1022*1024*1024):.1f} GB"


upload_handler = ConversationHandler(
    entry_points=[
        CommandHandler(
            "upload",
            check_tokens(0.1)(require_channel_membership(start_upload)),
        )
    ],
    states={
        UPLOADING: [
            MessageHandler(
                filters.PHOTO
                | filters.VIDEO
                | filters.AUDIO
                | filters.Document.ALL,
                handle_file,
            ),
            CommandHandler("cancel", cancel),
        ],
        CAPTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_caption),
            CommandHandler("cancel", cancel),
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
