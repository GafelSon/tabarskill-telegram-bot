# time handler function

# main lib
from datetime import datetime

# dependencies lib
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from telegram.ext import ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

# local lib
from app.core.log import internal_error
from app.core.logger import logger
from app.utils.escape import markdownES as mds
from app.utils.jalali import jcal, calendar  # ![TODO] calendar not exist right now
from app.database.models.enums import RoleType, EventType
from app.database.models import ProfileModel, EventModel
from app.services.iran_holidays import IranHolidaysService

holidays_service = IranHolidaysService()

# logger config
logger = logger(__name__)


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    current_jalali = jcal._get_time()

    # ![TODO] make calendar class
    weekday = calendar.WEEKDAYS[current_jalali.weekday()]
    gregorian_date = current_jalali.togregorian()
    gregorian_month = calendar.GREGORIAN_MONTHS[gregorian_date.month]
    header, calendar_markup = calendar.get_month_calendar()

    async with context.db.session() as session:
        greeting = await _get_role(update.effective_user.id, session)

        await holidays_service.update()
        today_formatted = jcal.format(current_jalali, date_only=True)
        today_holidays = [
            h for h in holidays_service.holidays if h["jalali_date"] == today_formatted
        ]

        today_start = datetime.combine(gregorian_date, datetime.min.time())
        today_end = datetime.combine(gregorian_date, datetime.max.time())

        db_events_result = await session.execute(
            select(EventModel).where(
                and_(EventModel.date >= today_start, EventModel.date <= today_end)
            )
        )
        db_events = db_events_result.scalars().all()

        personal_events = [
            e
            for e in db_events
            if e.type == EventType.PERSONAL
            and e.created_by == str(update.effective_user.id)
        ]
        university_events = [e for e in db_events if e.type == EventType.UNIVERSITY]
        national_events = [e for e in db_events if e.type == EventType.NATIONAL]
        events_sections = []

        # National holidays
        if today_holidays:
            holidays_text = "\n".join(
                [
                    f"🔸 {mds(h['title'])}" + (" \(تعطیل\)" if h["is_holiday"] else "")
                    for h in today_holidays
                ]
            )
            events_sections.append(f"🏛️ *رویدادهای ملی:*\n{holidays_text}")

        # National events
        if national_events:
            national_text = "\n".join(
                [
                    f"🔸 {mds(e.title)}"
                    + (
                        f" - {e.date.strftime('%H:%M')}"
                        if e.date.time() != datetime.min.time()
                        else ""
                    )
                    for e in national_events
                ]
            )
            if not today_holidays:
                events_sections.append(f"🏛️ *رویدادهای ملی:*\n{national_text}")
            else:
                events_sections[-1] += f"\n{national_text}"

        # University events
        if university_events:
            university_text = "\n".join(
                [
                    f"🔸 {mds(e.title)}"
                    + (
                        f" - {e.date.strftime('%H:%M')}"
                        if e.date.time() != datetime.min.time()
                        else ""
                    )
                    for e in university_events
                ]
            )
            events_sections.append(f"🎓 *رویدادهای دانشگاهی:*\n{mds(university_text)}")

        # Personal events
        if personal_events:
            personal_text = "\n".join(
                [
                    f"🔸 {mds(e.title)}"
                    + (
                        f" - {e.date.strftime('%H:%M')}"
                        if e.date.time() != datetime.min.time()
                        else ""
                    )
                    for e in personal_events
                ]
            )
            events_sections.append(f"👤 *رویدادهای شخصی:*\n{mds(personal_text)}")

        if events_sections:
            events_text = "\n\n".join(events_sections)
        else:
            events_text = "هیچ رویدادی برای امروز ثبت نشده است"

        onboarding = (
            f">تقویم دانشجویی\n\n\n"
            f"👋 *{greeting} وقت بخیر*\n\n"
            f"💫 امروز {weekday}\n"
            f"☀️ {current_jalali.day} {calendar.MONTH_NAMES[current_jalali.month - 1]} ماه {current_jalali.year} هجری شمسی\n"
            f"🌲 {gregorian_date.day} {gregorian_month} {gregorian_date.year} میلادی\n\n"
            f"🗓️ *لیست رویدادهای امروز:*\n"
            f"{events_text}\n\n"
            f">روش سپری کردن زمان است که شخصیت ما را تعریف می‌کند – جاناتان استرین"
        )  # ![TODO] use onother api for qoute...

        keyboard = [
            [
                InlineKeyboardButton("⚙️ مدیریت", callback_data="settings_calendar"),
                InlineKeyboardButton("🗓️ تقویم", callback_data="show_calendar"),
            ]
        ]

        keyboard_layout = InlineKeyboardMarkup(keyboard)

        await update.message.reply_photo(
            photo=calendar.fetch_season_theme_image(),
            caption=onboarding,
            parse_mode="MarkdownV2",
            reply_markup=keyboard_layout,
        )


async def _get_role(telegram_id: int, session: AsyncSession) -> str:
    try:
        result = await session.execute(
            select(ProfileModel).where(ProfileModel.telegram_id == str(telegram_id))
        )
        profile = result.scalar_one_or_none()

        if not profile:
            return "کاربر گرامی"

        if profile.role == RoleType.PROFESSOR:
            return "استاد گرامی"
        elif profile.role == RoleType.STUDENT:
            return "دانشجوی عزیز"
        elif profile.role == RoleType.SUPPORT:
            return "پشتیبان گرامی"
        else:
            return "کاربر گرامی"

    except Exception as e:
        logger.error(
            f"SYSTEM:: TimeHandler:: GetRole:: Error fetching user role for {telegram_id}: {e}"
        )
        return "کاربر گرامی"
