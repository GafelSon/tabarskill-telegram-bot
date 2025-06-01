import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import uuid
import asyncio

from telegram import (
    Message,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InlineQueryResultDocument,
    InputTextMessageContent,
    InputFile,
)
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    InlineQueryHandler,
    filters,
)

from app.core.decor import message_object

logger = logging.getLogger(__name__)

# Constants
FILE_IDS_PATH = Path("app/database/file.json")
VALID_CATEGORIES = ["major", "university", "faculty", "filename"]
CATEGORY_MAP = {
    "search_major": "major",
    "search_university": "university",
    "search_faculty": "faculty",
    "search_filename": "filename",
}


class FileSearch:
    @staticmethod
    def load_file_data() -> Dict:
        try:
            with open(FILE_IDS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data.get("files"), list):
                    logger.error("Invalid data structure: 'files' is not a list")
                    return {"files": [], "statistics": {}}
                logger.info(f"Loaded {len(data.get('files', []))} files from database")
                return data
        except Exception as e:
            logger.error(f"Error loading file data: {e}")
            return {"files": [], "statistics": {}}

    @staticmethod
    def format_file_info(file_data: Dict) -> str:
        user_info = file_data.get("user_info", {})
        return (
            f"📄 *{file_data.get('original_filename', 'نامشخص')}*\n"
            f"🏛️ *دانشگاه:* {user_info.get('university', 'نامشخص')}\n"
            f"🔬 *دانشکده:* {user_info.get('faculty', 'نامشخص')}\n"
            f"📚 *رشته:* {user_info.get('major', 'نامشخص')}\n"
            f"👤 *آپلود کننده:* {user_info.get('uploader_name', 'نامشخص')}\n"
            f"⏱️ *زمان آپلود:* {file_data.get('upload_date', 'نامشخص')}\n"
            f"📝 *توضیحات:* {file_data.get('caption', 'بدون توضیحات')}\n"
            f"⚠️ *توجه:* این فایل پس از ۶۰ ثانیه حذف خواهد شد. لطفاً آن را ذخیره کنید.\n"
        )

    @staticmethod
    def search_files(search_type: str, search_term: str) -> List[Dict]:
        data = FileSearch.load_file_data()
        files = data.get("files", [])

        if not isinstance(files, list):
            logger.error("Files is not a list")
            return []

        logger.info(f"Searching for '{search_term}' in category '{search_type}'")
        results = []

        if not search_term:
            return files[:50]

        for file in files:
            try:
                user_info = file.get("user_info", {})

                if search_type == "major":
                    if search_term.lower() in user_info.get("major", "").lower():
                        results.append(file)
                elif search_type == "university":
                    if search_term.lower() in user_info.get("university", "").lower():
                        results.append(file)
                elif search_type == "faculty":
                    if search_term.lower() in user_info.get("faculty", "").lower():
                        results.append(file)
                elif search_type == "filename":
                    if (
                        search_term.lower() in file.get("original_filename", "").lower()
                        or search_term.lower() in file.get("title", "").lower()
                    ):
                        results.append(file)
            except Exception as e:
                logger.error(f"Error processing file: {e}")
                continue

        logger.info(f"Found {len(results)} results")
        return results[:50]


class KeyboardBuilder:
    @staticmethod
    def create_category_keyboard() -> InlineKeyboardMarkup:
        keyboard = [
            [
                InlineKeyboardButton(
                    "🔍 جستجو بر اساس رشته", callback_data="search_major"
                ),
                InlineKeyboardButton(
                    "🏛️ جستجو بر اساس دانشگاه", callback_data="search_university"
                ),
            ],
            [
                InlineKeyboardButton(
                    "🔬 جستجو بر اساس دانشکده", callback_data="search_faculty"
                ),
                InlineKeyboardButton(
                    "📝 جستجو بر اساس نام فایل", callback_data="search_filename"
                ),
            ],
            [InlineKeyboardButton("📚 همه منابع", callback_data="show_all")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def create_download_keyboard(file_id: str) -> InlineKeyboardMarkup:
        safe_file_id = str(file_id).strip()
        callback_data = f"dl_{safe_file_id[:32]}"
        keyboard = [
            [
                InlineKeyboardButton("⬇️ دانلود فایل", callback_data=callback_data),
                InlineKeyboardButton(
                    "💾 ذخیره فایل", callback_data=f"save_{safe_file_id[:32]}"
                ),
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def create_file_info_keyboard(file_id: str) -> InlineKeyboardMarkup:
        safe_file_id = str(file_id).strip()
        callback_data = f"dl_{safe_file_id[:32]}"
        keyboard = [
            [
                InlineKeyboardButton(
                    "📋 مشاهده اطلاعات", callback_data=f"info_{safe_file_id[:32]}"
                ),
                InlineKeyboardButton("⬇️ دانلود فایل", callback_data=callback_data),
            ],
            [
                InlineKeyboardButton(
                    "💾 ذخیره فایل", callback_data=f"save_{safe_file_id[:32]}"
                ),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)


class MessageBuilder:
    @staticmethod
    def get_help_message(bot_username: str = None) -> str:
        base_message = (
            "🔍 *راهنمای جستجوی منابع*\n\n"
            "برای جستجو از فرمت زیر استفاده کنید:\n"
            "#category:search_term\n\n"
            "مثال‌ها:\n"
            "#major:algorithms\n"
            "#university:دانشگاه ملی مهارت\n"
            "#faculty:امام محمد باقر\n"
            "#filename:انقلاب\n\n"
            "دسته‌بندی‌های مجاز:\n"
            "- major\n"
            "- university\n"
            "- faculty\n"
            "- filename\n\n"
            "همچنین می‌توانید از جستجوی درون خطی (inline) استفاده کنید:\n"
            "@tabarskillbot search:term\n"
            "@tabarskillbot #category:term\n"
        )

        if bot_username:
            base_message += f"💡 *نکته:* می‌توانید از دستور /source هم استفاده کنید."
            return base_message.replace("#", f"@{bot_username} #")
        return base_message

    @staticmethod
    def get_invalid_format_message(bot_username: str = None) -> str:
        base_message = (
            "❌ فرمت جستجو نادرست است.\n"
            "لطفاً از فرمت زیر استفاده کنید:\n"
            "#category:search_term\n\n"
            "مثال‌ها:\n"
            "#major:algorithms\n"
            "#university:دانشگاه ملی مهارت\n"
            "#faculty:امام محمد باقر\n"
            "#filename:انقلاب"
        )

        if bot_username:
            return base_message.replace("#", f"@{bot_username} #")
        return base_message

    @staticmethod
    def get_invalid_category_message() -> str:
        return (
            "❌ دسته‌بندی نامعتبر است.\n"
            "دسته‌بندی‌های مجاز:\n"
            "- major\n"
            "- university\n"
            "- faculty\n"
            "- filename"
        )

    @staticmethod
    def get_no_results_message(search_term: str, search_type: str) -> str:
        return f"🔍 هیچ منبعی برای جستجوی '{search_term}' در دسته‌بندی '{search_type}' یافت نشد."


async def send_file_card(file_data, context, chat_id, reply_markup=None):
    title = file_data.get("title", file_data.get("original_filename", "عنوان نامشخص"))
    year = file_data.get("year", "")
    rating = file_data.get("rating", "")
    updated = file_data.get("last_update", file_data.get("upload_date", "تاریخ نامشخص"))
    description = file_data.get("description", file_data.get("caption", ""))
    genres = file_data.get("genres", [])
    poster_url = file_data.get("poster", None)

    caption = f"🎬 *{title}*"
    if year:
        caption += f" ({year})"
    if rating:
        caption += f" • ⭐️ {rating}/10"
    caption += f"\n🕰 بروزرسانی: {updated}\n"
    if description:
        caption += f"{description}\n"
    if genres:
        caption += f"\n🎭 _{'، '.join(genres)}_"

    if poster_url:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=poster_url,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=caption,
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )


async def send_file_cards(files, context, chat_id, with_download_button=False):
    for file_data in files:
        reply_markup = None
        if with_download_button and file_data.get("file_id"):
            reply_markup = KeyboardBuilder.create_download_keyboard(
                file_data["file_id"]
            )
        await send_file_card(file_data, context, chat_id, reply_markup=reply_markup)
        await asyncio.sleep(0.5)


class SourceHandler:
    @staticmethod
    @message_object
    async def handle_source_command(
        update: Update, context: ContextTypes.DEFAULT_TYPE, message: Message = None
    ) -> None:
        """Handle the /source command."""
        if not update.effective_message:
            return

        if context.args:
            search_query = " ".join(context.args)
            if ":" in search_query:
                search_type, search_term = search_query.split(":", 1)
                search_type = search_type.strip().lower()
                search_term = search_term.strip()

                logger.info(
                    f"Processing search: type={search_type}, term={search_term}"
                )

                if search_type not in VALID_CATEGORIES:
                    await update.effective_message.reply_text(
                        MessageBuilder.get_invalid_category_message()
                    )
                    return

                results = FileSearch.search_files(search_type, search_term)

                if not results:
                    await update.effective_message.reply_text(
                        MessageBuilder.get_no_results_message(search_term, search_type)
                    )
                    return

                await send_file_cards(
                    results,
                    context,
                    update.effective_chat.id,
                    with_download_button=True,
                )
                return
            else:
                await update.effective_message.reply_text(
                    MessageBuilder.get_invalid_format_message()
                )
                return

        data = FileSearch.load_file_data()
        files = data.get("files", [])

        if not files:
            await update.effective_message.reply_text("هیچ منبعی یافت نشد.")
            return
        await update.effective_message.reply_text("در حال ارسال لیست منابع ...")

        for file_data in files[:50]:
            try:
                file_id = file_data.get("file_id")
                if not file_id:
                    continue

                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=file_id,
                    caption=(
                        f"📄 *{file_data.get('original_filename', 'نامشخص')}*\n\n"
                        f"{FileSearch.format_file_info(file_data)}"
                    ),
                    parse_mode="Markdown",
                )
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Error sending file: {e}")
                continue

    @staticmethod
    async def handle_source_callback(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        query = update.callback_query
        if not query:
            return

        await query.answer()
        data = FileSearch.load_file_data()
        files = data.get("files", [])

        if not isinstance(files, list):
            await query.edit_message_text("❌ خطا در داده‌های فایل.")
            return

        if query.data == "show_all":
            if not files:
                await query.edit_message_text("📭 هیچ منبعی یافت نشد.")
                return
            await query.edit_message_text("🔄 در حال ارسال لیست منابع ...")
            for file_data in files[:50]:
                try:
                    await context.bot.send_document(
                        chat_id=query.message.chat_id,
                        document=file_data["file_id"],
                        caption=(
                            f"📄 *{file_data.get('original_filename', 'نامشخص')}*\n\n"
                            f"{FileSearch.format_file_info(file_data)}"
                        ),
                        parse_mode="Markdown",
                    )
                    await asyncio.sleep(0.5)
                except Exception as e:
                    logger.error(f"Error sending file: {e}")
                    continue
            return

        if query.data.startswith("info_"):
            file_id = query.data.replace("info_", "")
            file_data = next((f for f in files if f.get("file_id") == file_id), None)

            if not file_data:
                await query.message.reply_text("[ ❌ ] اطلاعات فایل موجود نیست.")
                return

            file_info = FileSearch.format_file_info(file_data)
            await query.message.reply_text(
                file_info,
                parse_mode="Markdown",
                reply_markup=KeyboardBuilder.create_download_keyboard(file_id),
            )
            return

        if query.data.startswith("save_"):
            file_id = query.data.replace("save_", "")
            file_data = next(
                (f for f in files if f.get("file_id", "").startswith(file_id)), None
            )

            if not file_data:
                await query.message.reply_text("❌ متأسفانه این فایل در دسترس نیست.")
                return

            await query.message.reply_text(
                "💾 فایل در سیستم شما ذخیره شد. می‌توانید آن را در هر زمان مشاهده کنید.",
                parse_mode="Markdown",
            )
            return

        category = CATEGORY_MAP.get(query.data)
        if not category:
            await query.edit_message_text("❌ دسته‌بندی نامعتبر است.")
            return

        category_files = []
        for file in files:
            user_info = file.get("user_info", {})
            if (
                category == "major"
                and user_info.get("major", "").lower().find(category.lower()) != -1
            ):
                category_files.append(file)
            elif (
                category == "university"
                and user_info.get("university", "").lower().find(category.lower()) != -1
            ):
                category_files.append(file)
            elif (
                category == "faculty"
                and user_info.get("faculty", "").lower().find(category.lower()) != -1
            ):
                category_files.append(file)
            elif (
                category == "filename"
                and file.get("original_filename", "").lower().find(category.lower())
                != -1
            ):
                category_files.append(file)

        if not category_files:
            await query.edit_message_text(
                f"📭 هیچ منبعی در دسته‌بندی {category} یافت نشد."
            )
            return

        await query.edit_message_text(f"🔄 در حال ارسال فایل‌های دسته‌بندی {category}...")
        # Send files directly
        for file_data in category_files[:50]:
            try:
                await context.bot.send_document(
                    chat_id=query.message.chat_id,
                    document=file_data["file_id"],
                    caption=(
                        f"📄 *{file_data.get('original_filename', 'نامشخص')}*\n\n"
                        f"{FileSearch.format_file_info(file_data)}"
                    ),
                    parse_mode="Markdown",
                )
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Error sending file: {e}")
                continue

    @staticmethod
    async def handle_download_callback(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        query = update.callback_query
        if not query:
            return

        await query.answer()
        file_id = query.data.replace("dl_", "")

        data = FileSearch.load_file_data()
        file_data = next(
            (
                f
                for f in data.get("files", [])
                if f.get("file_id", "").startswith(file_id)
            ),
            None,
        )

        if not file_data:
            await query.message.reply_text(
                "❌ متأسفانه این فایل در دسترس نیست. ممکن است حذف شده باشد."
            )
            return

        try:
            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=file_data["file_id"],
                caption=(
                    f"📄 *{file_data.get('original_filename', 'نامشخص')}*\n\n"
                    f"⚠️ *توجه:* این فایل پس از ۶۰ ثانیه حذف خواهد شد. لطفاً آن را ذخیره کنید."
                ),
                parse_mode="Markdown",
                reply_markup=KeyboardBuilder.create_download_keyboard(file_id),
            )
        except Exception as e:
            logger.error(f"Error sending file: {e}")
            await query.message.reply_text(
                f"❌ متأسفانه در ارسال فایل '{file_data.get('original_filename', 'نامشخص')}' مشکلی پیش آمده است. لطفاً دوباره تلاش کنید."
            )


source_handler = CommandHandler("source", SourceHandler.handle_source_command)
source_callback_handler = CallbackQueryHandler(
    SourceHandler.handle_source_callback, pattern="^(search_|show_all|info_|save_)"
)
download_handler = CallbackQueryHandler(
    SourceHandler.handle_download_callback, pattern="^dl_"
)
