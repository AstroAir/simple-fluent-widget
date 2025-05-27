"""
Fluent Design Style Data Formatting Utilities
Data formatting and display utilities for consistent presentation
"""

from PySide6.QtCore import QDateTime, QDate, QTime, QLocale, Qt
from typing import List, Optional, Union
import re


class FluentDateTimeFormat:
    """Date and time formatting standards for Fluent Design"""

    # Date formats
    SHORT_DATE = "MM/dd/yyyy"  # 04/30/2023
    MEDIUM_DATE = "MMM d, yyyy"  # Apr 30, 2023
    LONG_DATE = "MMMM d, yyyy"  # April 30, 2023
    FULL_DATE = "dddd, MMMM d, yyyy"  # Sunday, April 30, 2023

    # Time formats
    SHORT_TIME = "h:mm AP"  # 2:30 PM
    MEDIUM_TIME = "h:mm:ss AP"  # 2:30:15 PM
    LONG_TIME = "h:mm:ss.zzz AP"  # 2:30:15.000 PM

    # Combined formats
    SHORT_DATETIME = "MM/dd/yyyy h:mm AP"  # 04/30/2023 2:30 PM
    MEDIUM_DATETIME = "MMM d, yyyy h:mm AP"  # Apr 30, 2023 2:30 PM
    LONG_DATETIME = "MMMM d, yyyy h:mm:ss AP"  # April 30, 2023 2:30:15 PM

    # Relative time formats
    RELATIVE_TODAY = "Today, {time}"  # Today, 2:30 PM
    RELATIVE_YESTERDAY = "Yesterday, {time}"  # Yesterday, 2:30 PM
    RELATIVE_TOMORROW = "Tomorrow, {time}"  # Tomorrow, 2:30 PM


class FluentNumberFormat:
    """Number formatting standards for Fluent Design"""

    # Number formats
    DECIMAL_ZERO = "{:.0f}"  # 1234
    DECIMAL_ONE = "{:.1f}"  # 1234.5
    DECIMAL_TWO = "{:.2f}"  # 1234.56

    # Thousand separators
    WITH_COMMAS = "{:,.2f}"  # 1,234.56
    WITH_SPACES = "{:,.2f}".replace(",", " ")  # 1 234.56

    # Currency
    CURRENCY_USD = "${:.2f}"  # $1234.56
    CURRENCY_EUR = "€{:.2f}"  # €1234.56
    CURRENCY_GBP = "£{:.2f}"  # £1234.56

    # File size
    FILESIZE_BYTES = "{} B"
    FILESIZE_KB = "{:.1f} KB"
    FILESIZE_MB = "{:.1f} MB"
    FILESIZE_GB = "{:.2f} GB"
    FILESIZE_TB = "{:.2f} TB"


class FluentFormatter:
    """Utility for formatting various data types according to Fluent Design standards"""

    def __init__(self, locale: Optional[QLocale] = None):
        """Initialize formatter with optional locale"""
        self._locale = locale or QLocale.system()

    def format_date(self, date: Union[QDate, QDateTime, str],
                    format_str: str = FluentDateTimeFormat.MEDIUM_DATE) -> str:
        """Format date according to specified format

        Args:
            date: Date to format (QDate, QDateTime, or ISO format string)
            format_str: Format string from FluentDateTimeFormat

        Returns:
            Formatted date string
        """
        if isinstance(date, str):
            qdate = QDate.fromString(date, Qt.DateFormat.ISODate)
            if not qdate.isValid():
                # Try datetime format
                qdatetime = QDateTime.fromString(date, Qt.DateFormat.ISODate)
                if qdatetime.isValid():
                    qdate = qdatetime.date()
                else:
                    return date  # Return original if parsing fails
        elif isinstance(date, QDateTime):
            qdate = date.date()
        else:
            qdate = date

        return self._locale.toString(qdate, format_str)

    def format_time(self, time: Union[QTime, QDateTime, str],
                    format_str: str = FluentDateTimeFormat.SHORT_TIME) -> str:
        """Format time according to specified format

        Args:
            time: Time to format (QTime, QDateTime, or ISO format string)
            format_str: Format string from FluentDateTimeFormat

        Returns:
            Formatted time string
        """
        if isinstance(time, str):
            qtime = QTime.fromString(time, Qt.DateFormat.ISODate)
            if not qtime.isValid():
                # Try datetime format
                qdatetime = QDateTime.fromString(time, Qt.DateFormat.ISODate)
                if qdatetime.isValid():
                    qtime = qdatetime.time()
                else:
                    return time  # Return original if parsing fails
        elif isinstance(time, QDateTime):
            qtime = time.time()
        else:
            qtime = time

        return self._locale.toString(qtime, format_str)

    def format_datetime(self, datetime: Union[QDateTime, str],
                        format_str: str = FluentDateTimeFormat.MEDIUM_DATETIME) -> str:
        """Format datetime according to specified format

        Args:
            datetime: Datetime to format (QDateTime or ISO format string)
            format_str: Format string from FluentDateTimeFormat

        Returns:
            Formatted datetime string
        """
        if isinstance(datetime, str):
            qdatetime = QDateTime.fromString(datetime, Qt.DateFormat.ISODate)
            if not qdatetime.isValid():
                return datetime  # Return original if parsing fails
        else:
            qdatetime = datetime

        return self._locale.toString(qdatetime, format_str)

    def format_relative_datetime(self, datetime: Union[QDateTime, str]) -> str:
        """Format datetime with relative indicators (Today, Yesterday, etc.)

        Args:
            datetime: Datetime to format (QDateTime or ISO format string)

        Returns:
            Formatted datetime with relative indicators where applicable
        """
        if isinstance(datetime, str):
            qdatetime = QDateTime.fromString(datetime, Qt.DateFormat.ISODate)
            if not qdatetime.isValid():
                return datetime  # Return original if parsing fails
        else:
            qdatetime = datetime

        today = QDate.currentDate()
        date = qdatetime.date()
        time_str = self.format_time(qdatetime.time())

        if date == today:
            return FluentDateTimeFormat.RELATIVE_TODAY.format(time=time_str)
        elif date == today.addDays(-1):
            return FluentDateTimeFormat.RELATIVE_YESTERDAY.format(time=time_str)
        elif date == today.addDays(1):
            return FluentDateTimeFormat.RELATIVE_TOMORROW.format(time=time_str)
        elif date.year() == today.year():
            # Same year, use medium date without year
            return f"{self._locale.toString(date, 'MMM d')} {time_str}"
        else:
            # Different year, use medium date
            return self.format_datetime(qdatetime, FluentDateTimeFormat.MEDIUM_DATETIME)

    def format_number(self, number: Union[int, float],
                      format_str: str = FluentNumberFormat.DECIMAL_TWO) -> str:
        """Format number according to specified format

        Args:
            number: Number to format
            format_str: Format string from FluentNumberFormat

        Returns:
            Formatted number string
        """
        return format_str.format(number)

    def format_filesize(self, size_bytes: int) -> str:
        """Format file size in human-readable format

        Args:
            size_bytes: Size in bytes

        Returns:
            Human-readable file size (e.g., "2.5 MB")
        """
        if size_bytes < 1024:
            return FluentNumberFormat.FILESIZE_BYTES.format(size_bytes)
        elif size_bytes < 1024 * 1024:
            return FluentNumberFormat.FILESIZE_KB.format(size_bytes / 1024)
        elif size_bytes < 1024 * 1024 * 1024:
            return FluentNumberFormat.FILESIZE_MB.format(size_bytes / (1024 * 1024))
        elif size_bytes < 1024 * 1024 * 1024 * 1024:
            return FluentNumberFormat.FILESIZE_GB.format(size_bytes / (1024 * 1024 * 1024))
        else:
            return FluentNumberFormat.FILESIZE_TB.format(size_bytes / (1024 * 1024 * 1024 * 1024))

    def format_phone(self, phone_number: str, country_code: str = "US") -> str:
        """Format phone number based on country code

        Args:
            phone_number: Phone number to format
            country_code: ISO country code (e.g., "US", "GB")

        Returns:
            Formatted phone number
        """
        # Remove non-digit characters
        digits = re.sub(r'\D', '', phone_number)

        if country_code == "US":
            if len(digits) == 10:
                return f"({digits[0:3]}) {digits[3:6]}-{digits[6:]}"
            else:
                return digits  # Return cleaned digits for non-standard lengths

        # Default fallback for other country codes
        return digits
