# Utils -> jalali module
# doc: https://pypi.org/project/jdatetime/

# dependencies lib
from datetime import timedelta, datetime
from jdatetime import datetime as jdatetime


class JalaliCalendar:
    WEEKDAYS = [
        "شنبه",
        "یکشنبه",
        "دوشنبه",
        "سه‌شنبه",
        "چهارشنبه",
        "پنج‌شنبه",
        "جمعه",
    ]

    MONTH_NAMES = [
        "فروردین",
        "اردیبهشت",
        "خرداد",
        "تیر",
        "مرداد",
        "شهریور",
        "مهر",
        "آبان",
        "آذر",
        "دی",
        "بهمن",
        "اسفند",
    ]

    GREGORIAN_MONTHS = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    SEASON_IMAGES = {
        "spring": "AgACAgQAAyEGAASLt5ydAANtaDKeP8MiUNCJIVZw2-qXsECkZUAAAmfGMRsx0phRVKlbrNh31PABAAMCAAN5AAM2BA",
        "summer": "AgACAgQAAyEGAASLt5ydAANvaDKeSoo7GwiFBOjhJWZ4jZl7LNsAAmjGMRsx0phRDTgjqgNJw_0BAAMCAAN5AAM2BA",
        "autumn": "AgACAgQAAyEGAASLt5ydAANraDKeNvQmCWJ-3ZjwvCeVQN2J1VwAAmbGMRsx0phRaPkhwbnOSIwBAAMCAAN5AAM2BA",
        "winter": "AgACAgQAAyEGAASLt5ydAANpaDKeBrA4gcwEropl1Pz-zlTFvxoAAmXGMRsx0phRolCVTVdwMVoBAAMCAAN5AAM2BA",
    }

    def fetch_season_theme_image(self) -> str:
        current = self._get_time()
        month = current.month

        if 1 <= month <= 3:
            return self.SEASON_IMAGES["spring"]
        elif 4 <= month <= 6:
            return self.SEASON_IMAGES["summer"]
        elif 7 <= month <= 9:
            return self.SEASON_IMAGES["autumn"]
        else:
            return self.SEASON_IMAGES["winter"]

    def get_month_calendar(self):
        current = self._get_time()
        month_name = self.MONTH_NAMES[current.month - 1]
        header = f"{month_name} {current.year}"
        first_day = jdatetime(current.year, current.month, 1)
        if current.month == 12:
            last_day = jdatetime(current.year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = jdatetime(current.year, current.month + 1, 1) - timedelta(days=1)

        calendar_grid = []
        current_row = []
        first_weekday = first_day.weekday()
        for _ in range(first_weekday):
            current_row.append(" ")
        for day in range(1, last_day.day + 1):
            if len(current_row) == 7:
                calendar_grid.append(current_row)
                current_row = []
            current_row.append(str(day))

        while len(current_row) < 7:
            current_row.append(" ")
        calendar_grid.append(current_row)
        calendar_markup = []
        calendar_markup.append(self.WEEKDAYS)
        calendar_markup.extend(calendar_grid)
        return header, calendar_markup

    def _get_time(self) -> jdatetime:
        """Returns the current Jalali date and time."""
        return jdatetime.now()

    def year(self) -> int:
        """Returns the current Jalali year."""
        return self._get_time().year

    def month(self) -> int:
        """Returns the current Jalali month."""
        return self._get_time().month

    def day(self) -> int:
        """Returns the current Jalali day."""
        return self._get_time().day

    def hour(self) -> int:
        """Returns the current hour."""
        return self._get_time().hour

    def minute(self) -> int:
        """Returns the current minute."""
        return self._get_time().minute

    def second(self) -> int:
        """Returns the current second."""
        return self._get_time().second

    @property
    def today(self) -> str:
        return self.format(jdatetime.now())

    def format(self, dt: jdatetime, date_only: bool = False) -> str:
        if date_only:
            return dt.strftime("%Y/%m/%d")
        return dt.strftime("%Y/%m/%d %H:%M:%S")

    def tab(self, dt) -> jdatetime:
        return jdatetime.fromgregorian(datetime=dt)

    def jalali_to_gregorian(self, jalali_date_str):
        """Convert a Jalali date string (YYYY/MM/DD) to a Gregorian datetime object."""
        try:
            parts = jalali_date_str.split("/")
            if len(parts) != 3:
                raise ValueError(f"Invalid Jalali date format: {jalali_date_str}")

            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            jalali_dt = jdatetime(year, month, day)

            return jalali_dt.togregorian()
        except Exception as e:
            print(f"Error converting Jalali date {jalali_date_str}: {str(e)}")
            return datetime.now()

    def gregorian_to_jalali(self, gregorian_date: datetime) -> jdatetime:
        """Convert a Gregorian datetime object to a Jalali datetime object."""
        try:
            return jdatetime.fromgregorian(datetime=gregorian_date)
        except Exception as e:
            print(f"Error converting Gregorian date {gregorian_date}: {str(e)}")
            return jdatetime.now()


# Initialize the JalaliCalendar instance
jcal = JalaliCalendar()
calendar = jcal

__all__ = ["jcal", "calendar"]
