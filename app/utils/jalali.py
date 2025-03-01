# app/utils/jalali.py
# doc: https://pypi.org/project/jdatetime/
from jdatetime import datetime as jdatetime

class JalaliCalendar:
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

# Initialize the JalaliCalendar instance
jcal = JalaliCalendar()

__all__ = ['jcal']