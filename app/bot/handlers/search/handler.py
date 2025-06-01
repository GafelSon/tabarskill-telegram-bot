# search handler

# main lib
import os
import time
import json
import hashlib
from datetime import datetime, timedelta

# dependencies lib
from telegram import (
    Update,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultCachedDocument,
    InlineQueryResultCachedPhoto,
    InlineQueryResultCachedVideo,
    InlineQueryResultCachedAudio,
)
from telegram.ext import ContextTypes, InlineQueryHandler, CallbackQueryHandler

# local lib
from app.core.logger import logger

# logger config
logger = logger(__name__)

# preInctance
JSON = "app/database/file.json"
_cache = {
    "data": None,
    "last_updated": None,
    "cache_duration": 60,
}


def load_files_from_cache():
    try:
        current_time = datetime.now()

        if (
            _cache["data"] is not None
            and _cache["last_updated"] is not None
            and current_time - _cache["last_updated"]
            < timedelta(seconds=_cache["cache_duration"])
        ):
            logger.info("SYSTEM:: Using cached data")
            return _cache["data"]
        if not os.path.exists(JSON):
            logger.warning(f"SYSTEM:: File {JSON} does not exist")
            return []

        with open(JSON, "r", encoding="utf-8") as f:
            data = json.load(f)

        files = data.get("files", [])

        _cache["data"] = files
        _cache["last_updated"] = current_time

        logger.info(
            f"SYSTEM:: Loaded {len(files)} files from database and updated cache"
        )
        return files

    except json.JSONDecodeError as e:
        logger.error(f"SYSTEM:: Invalid JSON in {JSON}: {e}")
        return []
    except Exception as e:
        logger.error(f"SYSTEM:: Error loading files: {e}")
        return []


def filter_files(files, query):
    if not query:
        return files[:10]

    query_lower = query.lower()
    filtered_files = []

    for file in files:
        filename = file.get("original_filename", "").lower()
        user_info = file.get("user_info", {})
        university = user_info.get("university", "").lower()
        faculty = user_info.get("faculty", "").lower()
        major = user_info.get("major", "").lower()

        if (
            query_lower in filename
            or query_lower in university
            or query_lower in faculty
            or query_lower in major
        ):
            filtered_files.append(file)
        if len(filtered_files) >= 10:
            break
    return filtered_files


def generate_unique_id(file_data, index):
    try:
        unique_string = f"{file_data.get('file_id', '')}{file_data.get('original_filename', '')}{index}"
        return hashlib.md5(unique_string.encode("utf-8")).hexdigest()
    except Exception:
        return f"file_{index}_{int(time.time())}"


async def inline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()

    try:
        query = update.inline_query.query.strip() if update.inline_query.query else ""
        logger.info(
            f"SYSTEM:: Inline query received: '{query}' from user {update.inline_query.from_user.id}"
        )

        results = []

        upload_id = generate_unique_id({"upload": True}, 999)
        results.append(
            InlineQueryResultArticle(
                id=upload_id,
                title="📤 آپلود فایل جدید",
                input_message_content=InputTextMessageContent(
                    message_text="برای آپلود فایل جدید، از دستور /upload استفاده کنید.",
                    parse_mode="Markdown",
                ),
                description="افزودن فایل جدید به آرشیو",
            )
        )

        all_files = load_files_from_cache()
        files = filter_files(all_files, query)[:5]
        logger.info(f"SYSTEM:: Found {len(files)} matching files for query: '{query}'")

        if not files:
            no_result_id = generate_unique_id({"no_results": True}, 0)
            results.append(
                InlineQueryResultArticle(
                    id=no_result_id,
                    title="❌ هیچ فایلی یافت نشد",
                    input_message_content=InputTextMessageContent(
                        message_text="❌ هیچ فایلی با این جستجو یافت نشد\n\n💡 نکات جستجو:\n• از کلمات کلیدی استفاده کنید\n• نام دانشگاه، دانشکده یا رشته را جستجو کنید\n• از بخشی از نام فایل استفاده کنید",
                        parse_mode="Markdown",
                    ),
                    description="نتیجه‌ای برای جستجوی شما یافت نشد",
                )
            )
        else:
            for idx, file in enumerate(files):
                try:
                    unique_id = generate_unique_id(file, idx)

                    file_type = file.get("file_type", "نامشخص")
                    filename = file.get("original_filename", "بدون نام")
                    user_info = file.get("user_info", {})
                    university = user_info.get("university", "نامشخص")
                    faculty = user_info.get("faculty", "نامشخص")

                    description = f"🏫 {university} | 📚 {faculty}"

                    file_type_emoji = "📄"
                    if file_type == "photo":
                        file_type_emoji = "🖼️"
                    elif file_type == "video":
                        file_type_emoji = "🎬"
                    elif file_type == "audio":
                        file_type_emoji = "🎵"

                    if file_type == "photo":
                        results.append(
                            InlineQueryResultCachedPhoto(
                                id=unique_id,
                                photo_file_id=file.get("file_id"),
                                title=f"{file_type_emoji} {filename[:100]}",
                                description=description[:100],
                                caption=f"{file_type_emoji} *{filename}*\n📊 *نوع فایل:* عکس",
                                parse_mode="Markdown",
                            )
                        )
                    elif file_type == "video":
                        results.append(
                            InlineQueryResultCachedVideo(
                                id=unique_id,
                                video_file_id=file.get("file_id"),
                                title=f"{file_type_emoji} {filename[:100]}",
                                description=description[:100],
                                caption=f"{file_type_emoji} *{filename}*\n📊 *نوع فایل:* ویدیو",
                                parse_mode="Markdown",
                            )
                        )
                    elif file_type == "audio":
                        results.append(
                            InlineQueryResultCachedAudio(
                                id=unique_id,
                                audio_file_id=file.get("file_id"),
                                title=f"{file_type_emoji} {filename[:100]}",
                                caption=f"{file_type_emoji} *{filename}*\n📊 *نوع فایل:* صوت",
                                parse_mode="Markdown",
                            )
                        )
                    else:
                        results.append(
                            InlineQueryResultCachedDocument(
                                id=unique_id,
                                title=f"{file_type_emoji} {filename[:100]}",
                                document_file_id=file.get("file_id"),
                                description=description[:100],
                                caption=f"{file_type_emoji} *{filename}*\n📊 *نوع فایل:* {file_type}",
                                parse_mode="Markdown",
                            )
                        )

                except Exception as e:
                    logger.error(f"SYSTEM:: Error processing file {idx}: {e}")
                    continue

        processing_time = time.time() - start_time
        logger.info(
            f"SYSTEM:: Processing completed in {processing_time:.2f} seconds. Sending {len(results)} results"
        )

        if processing_time < 3.0:
            cache_time = 60 if query else 30
            await update.inline_query.answer(results, cache_time=cache_time)
        else:
            logger.warning(
                f"SYSTEM:: Processing took too long ({processing_time:.2f}s), sending limited response"
            )
            limited_results = results[:2] if len(results) > 2 else results
            await update.inline_query.answer(limited_results, cache_time=10)

    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            f"SYSTEM:: Critical error in inline_handlerafter {processing_time:.2f}s: {e}"
        )

        try:
            error_id = generate_unique_id({"error": True}, 0)
            error_result = InlineQueryResultArticle(
                id=error_id,
                title="خطا در جستجو",
                input_message_content=InputTextMessageContent(
                    message_text="[ ❌ ] خطایی در جستجو رخ داد. لطفاً دوباره تلاش کنید.",
                    parse_mode="Markdown",
                ),
                description="خطا در سیستم جستجو",
            )
            await update.inline_query.answer([error_result], cache_time=1)
        except Exception as final_error:
            logger.error(f"SYSTEM:: Failed to send error response: {final_error}")
            try:
                await update.inline_query.answer([], cache_time=1)
            except:
                pass


def setup_inline_handler(application):
    try:
        application.add_handler(InlineQueryHandler(inline_handler))
        logger.info("SYSTEM:: Inline query handler registered successfully")

        if os.path.exists(JSON):
            try:
                with open(JSON, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    files_count = len(data.get("files", []))
                    logger.info(
                        f"SYSTEM:: Database loaded successfully with {files_count} files"
                    )
            except Exception as e:
                logger.error(f"SYSTEM:: Database file exists but has issues: {e}")
        else:
            logger.warning(f"SYSTEM:: Database file {JSON} not found")

    except Exception as e:
        logger.error(f"SYSTEM:: Failed to setup inline handler: {e}")
        raise


async def handle_file_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        callback_data = query.data
        if callback_data.startswith("download_"):
            file_id = callback_data[9:]

            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="🔄 در حال دریافت فایل...",
                parse_mode="Markdown",
            )

            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=file_id,
                caption="✅ فایل با موفقیت دریافت شد.",
            )
    except Exception as e:
        logger.error(f"SYSTEM:: Error handling file download: {e}")
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="[ ❌ ] خطا در دریافت فایل. لطفاً دوباره تلاش کنید.",
            parse_mode="Markdown",
        )
