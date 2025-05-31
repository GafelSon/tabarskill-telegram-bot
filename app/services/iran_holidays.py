# Services - iran holiday

# main lib
import os
import json
import aiohttp
import asyncio
from dotenv import load_dotenv
from datetime import datetime, timedelta

# local lib
from app.core.logger import logger
from app.utils.jalali import jcal

# config logger
# Load environment variables from .env file
load_dotenv()
logger = logger(__name__)

# preInstance
HOLIDAY_API_BASE_URL = os.getenv("HOLIDAY_API_BASE_URL", "")


class IranHolidaysService:
    def __init__(self):
        self.base_url = HOLIDAY_API_BASE_URL
        self.last_update = None
        self.holidays = []

    async def fetch_for_date(self, jalali_date):
        logger.info(
            f"SYSTEM:: Services:: IranHolidays:: Fetching holidays for Jalali date {jalali_date}"
        )
        holidays = []

        try:
            if " " in jalali_date:
                jalali_date = jalali_date.split(" ")[0]

            parts = jalali_date.split("/")
            if len(parts) != 3:
                logger.error(
                    f"SYSTEM:: Services:: IranHolidays:: Invalid date format: {jalali_date}"
                )
                return []

            year = parts[0]
            month = parts[1]
            day = parts[2]

            if len(month) == 1:
                month = f"0{month}"
            if len(day) == 1:
                day = f"0{day}"

            formatted_date = f"{year}/{month}/{day}"

            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/{formatted_date}"
                try:
                    async with session.get(
                        url, timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status == 429:
                            logger.warning(
                                f"SYSTEM:: Services:: IranHolidays:: Rate limit hit for {url}, waiting 3 seconds"
                            )
                            await asyncio.sleep(3)
                            return []

                        if response.status == 200:
                            data = await response.json()
                            gregorian_date = jcal.jalali_to_gregorian(formatted_date)
                            is_holiday = data.get("is_holiday", False)
                            for event in data.get("events", []):
                                holidays.append(
                                    {
                                        "title": event.get("description", ""),
                                        "date": gregorian_date,
                                        "is_holiday": is_holiday
                                        or event.get("is_holiday", False),
                                        "is_religious": event.get(
                                            "is_religious", False
                                        ),
                                        "additional_description": event.get(
                                            "additional_description", ""
                                        ),
                                        "jalali_date": formatted_date,
                                    }
                                )
                            if is_holiday and not data.get("events"):
                                holidays.append(
                                    {
                                        "title": "تعطیل رسمی",
                                        "date": gregorian_date,
                                        "is_holiday": True,
                                        "is_religious": False,
                                        "additional_description": "",
                                        "jalali_date": formatted_date,
                                    }
                                )
                        else:
                            logger.error(
                                f"SYSTEM:: Services:: IranHolidays:: Failed to fetch holidays for {formatted_date}: HTTP {response.status}"
                            )
                except asyncio.TimeoutError:
                    logger.error(
                        f"SYSTEM:: Services:: IranHolidays:: Timeout while fetching holidays for {formatted_date}"
                    )
                except Exception as e:
                    logger.error(
                        f"SYSTEM:: Services:: IranHolidays:: Error during API request for {formatted_date}: {str(e)}"
                    )
            return holidays

        except Exception as e:
            logger.error(
                f"SYSTEM:: Services:: IranHolidays:: Error fetching Iranian holidays: {str(e)}"
            )
            return []

    async def update(self):
        current_jalali_date = jcal.today
        if self.last_update and (datetime.now() - self.last_update).days < 1:
            logger.info("Already updated holidays today, skipping")
            return 0
        holidays = await self.fetch_for_date(current_jalali_date)

        if holidays:
            self.holidays = [
                h for h in self.holidays if h["jalali_date"] != current_jalali_date
            ]
            self.holidays.extend(holidays)
            self.last_update = datetime.now()

        return len(holidays)
