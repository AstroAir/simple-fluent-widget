import pytest
import sys
import os
from PySide6.QtCore import QDate, QTime, QDateTime, QLocale, Qt
from .formatters import FluentFormatter, FluentDateTimeFormat, FluentNumberFormat, DateLike, TimeLike, DateTimeLike, NumericValue

# Add the parent directory to the path for relative import if necessary
# Assuming the test file is components/data/test_formatters.py
# and the module is components/data/formatters.py
# The parent directory 'data' is a package (__init__.py exists)
# So we can use relative import
try:
except ImportError as e:
    pytest.fail(f"Failed to import components: {e}")

# pytest-qt provides the qapp fixture automatically

class TestFluentFormatter:

    def test_initialization(self, qapp):
        """Test FluentFormatter initialization."""
        formatter = FluentFormatter()
        assert isinstance(formatter, FluentFormatter)
        assert isinstance(formatter._locale, QLocale)
        # Test with a specific locale
        locale_us = QLocale(QLocale.Language.English, QLocale.Country.UnitedStates)
        formatter_us = FluentFormatter(locale=locale_us)
        assert formatter_us._locale.country() == QLocale.Country.UnitedStates

    @pytest.mark.parametrize("input_date, format_str, expected_output", [
        (QDate(2023, 4, 30), FluentDateTimeFormat.SHORT_DATE, "04/30/2023"),
        (QDate(2023, 4, 30), FluentDateTimeFormat.MEDIUM_DATE, "Apr 30, 2023"),
        (QDate(2023, 4, 30), FluentDateTimeFormat.LONG_DATE, "April 30, 2023"),
        (QDate(2023, 4, 30), FluentDateTimeFormat.FULL_DATE, "Sunday, April 30, 2023"),
        ("2023-04-30", FluentDateTimeFormat.SHORT_DATE, "04/30/2023"), # ISO string date
        ("2023-04-30T14:30:00", FluentDateTimeFormat.MEDIUM_DATE, "Apr 30, 2023"), # ISO string datetime
        (QDateTime(2023, 4, 30, 14, 30, 0), FluentDateTimeFormat.LONG_DATE, "April 30, 2023"), # QDateTime object
        ("invalid-date-string", FluentDateTimeFormat.SHORT_DATE, "invalid-date-string"), # Invalid string
        (None, FluentDateTimeFormat.SHORT_DATE, ""), # None input (QDate.toString handles this)
    ])
    def test_format_date(self, qapp, input_date: DateLike, format_str: str, expected_output: str):
        """Test format_date method."""
        formatter = FluentFormatter(locale=QLocale(QLocale.Language.English, QLocale.Country.UnitedStates)) # Use US locale for predictable output
        # QDate.toString(None) returns an empty string, which matches the expected behavior for invalid dates
        # For string inputs that fail parsing, the original string is returned.
        if input_date is None:
             qdate_input = QDate() # Represents an invalid date
        elif isinstance(input_date, str):
             qdate_input = input_date # Pass string directly to method
        elif isinstance(input_date, QDateTime):
             qdate_input = input_date # Pass QDateTime directly
        else:
             qdate_input = input_date # Pass QDate directly

        result = formatter.format_date(qdate_input, format_str)

        # Handle potential locale differences for day/month names if not using a fixed locale
        # With fixed US locale, output should be exact
        assert result == expected_output

    @pytest.mark.parametrize("input_time, format_str, expected_output", [
        (QTime(14, 30, 0), FluentDateTimeFormat.SHORT_TIME, "2:30 PM"),
        (QTime(14, 30, 15), FluentDateTimeFormat.MEDIUM_TIME, "2:30:15 PM"),
        (QTime(14, 30, 15, 123), FluentDateTimeFormat.LONG_TIME, "2:30:15.123 PM"),
        ("14:30:00", FluentDateTimeFormat.SHORT_TIME, "2:30 PM"), # ISO string time
        ("2023-04-30T14:30:00", FluentDateTimeFormat.MEDIUM_TIME, "2:30:00 PM"), # ISO string datetime
        (QDateTime(2023, 4, 30, 14, 30, 15), FluentDateTimeFormat.LONG_TIME, "2:30:15.000 PM"), # QDateTime object
        ("invalid-time-string", FluentDateTimeFormat.SHORT_TIME, "invalid-time-string"), # Invalid string
        (None, FluentDateTimeFormat.SHORT_TIME, ""), # None input (QTime.toString handles this)
    ])
    def test_format_time(self, qapp, input_time: TimeLike, format_str: str, expected_output: str):
        """Test format_time method."""
        formatter = FluentFormatter(locale=QLocale(QLocale.Language.English, QLocale.Country.UnitedStates)) # Use US locale
        if input_time is None:
             qtime_input = QTime() # Represents an invalid time
        elif isinstance(input_time, str):
             qtime_input = input_time # Pass string directly
        elif isinstance(input_time, QDateTime):
             qtime_input = input_time # Pass QDateTime directly
        else:
             qtime_input = input_time # Pass QTime directly

        result = formatter.format_time(qtime_input, format_str)
        assert result == expected_output

    @pytest.mark.parametrize("input_datetime, format_str, expected_output", [
        (QDateTime(2023, 4, 30, 14, 30, 0), FluentDateTimeFormat.SHORT_DATETIME, "04/30/2023 2:30 PM"),
        (QDateTime(2023, 4, 30, 14, 30, 0), FluentDateTimeFormat.MEDIUM_DATETIME, "Apr 30, 2023 2:30 PM"),
        (QDateTime(2023, 4, 30, 14, 30, 15), FluentDateTimeFormat.LONG_DATETIME, "April 30, 2023 2:30:15 PM"),
        ("2023-04-30T14:30:00", FluentDateTimeFormat.SHORT_DATETIME, "04/30/2023 2:30 PM"), # ISO string
        ("invalid-datetime-string", FluentDateTimeFormat.SHORT_DATETIME, "invalid-datetime-string"), # Invalid string
        (None, FluentDateTimeFormat.SHORT_DATETIME, ""), # None input (QDateTime.toString handles this)
    ])
    def test_format_datetime(self, qapp, input_datetime: DateTimeLike, format_str: str, expected_output: str):
        """Test format_datetime method."""
        formatter = FluentFormatter(locale=QLocale(QLocale.Language.English, QLocale.Country.UnitedStates)) # Use US locale
        if input_datetime is None:
             qdatetime_input = QDateTime() # Represents an invalid datetime
        elif isinstance(input_datetime, str):
             qdatetime_input = input_datetime # Pass string directly
        else:
             qdatetime_input = input_datetime # Pass QDateTime directly

        result = formatter.format_datetime(qdatetime_input, format_str)
        assert result == expected_output

    def test_format_relative_datetime(self, qapp):
        """Test format_relative_datetime method."""
        formatter = FluentFormatter(locale=QLocale(QLocale.Language.English, QLocale.Country.UnitedStates)) # Use US locale

        now = QDateTime.currentDateTime()
        today_dt = QDateTime(now.date(), QTime(10, 0, 0))
        yesterday_dt = QDateTime(now.date().addDays(-1), QTime(15, 30, 0))
        tomorrow_dt = QDateTime(now.date().addDays(1), QTime(8, 0, 0))
        same_year_dt = QDateTime(QDate(now.date().year(), 1, 15), QTime(12, 0, 0))
        diff_year_dt = QDateTime(QDate(now.date().year() - 1, 12, 25), QTime(20, 0, 0))

        # Test Today
        result_today = formatter.format_relative_datetime(today_dt)
        expected_today_time = formatter.format_time(today_dt.time())
        assert result_today == FluentDateTimeFormat.RELATIVE_TODAY.format(time=expected_today_time)

        # Test Yesterday
        result_yesterday = formatter.format_relative_datetime(yesterday_dt)
        expected_yesterday_time = formatter.format_time(yesterday_dt.time())
        assert result_yesterday == FluentDateTimeFormat.RELATIVE_YESTERDAY.format(time=expected_yesterday_time)

        # Test Tomorrow
        result_tomorrow = formatter.format_relative_datetime(tomorrow_dt)
        expected_tomorrow_time = formatter.format_time(tomorrow_dt.time())
        assert result_tomorrow == FluentDateTimeFormat.RELATIVE_TOMORROW.format(time=expected_tomorrow_time)

        # Test Same Year (not today, yesterday, tomorrow)
        result_same_year = formatter.format_relative_datetime(same_year_dt)
        expected_same_year_date = formatter._locale.toString(same_year_dt.date(), 'MMM d')
        expected_same_year_time = formatter.format_time(same_year_dt.time())
        assert result_same_year == f"{expected_same_year_date} {expected_same_year_time}"

        # Test Different Year
        result_diff_year = formatter.format_relative_datetime(diff_year_dt)
        expected_diff_year_datetime = formatter.format_datetime(diff_year_dt, FluentDateTimeFormat.MEDIUM_DATETIME)
        assert result_diff_year == expected_diff_year_datetime

        # Test ISO string input
        iso_string_today = now.toString(Qt.DateFormat.ISODate)
        result_iso_today = formatter.format_relative_datetime(iso_string_today)
        expected_iso_today_time = formatter.format_time(now.time())
        assert result_iso_today == FluentDateTimeFormat.RELATIVE_TODAY.format(time=expected_iso_today_time)

        # Test invalid string input
        result_invalid_string = formatter.format_relative_datetime("invalid-string")
        assert result_invalid_string == "invalid-string"

    @pytest.mark.parametrize("input_number, format_str, expected_output", [
        (1234.567, FluentNumberFormat.DECIMAL_ZERO, "1235"), # Rounds up
        (1234.567, FluentNumberFormat.DECIMAL_ONE, "1234.6"), # Rounds up
        (1234.567, FluentNumberFormat.DECIMAL_TWO, "1234.57"), # Rounds up
        (1234567.89, FluentNumberFormat.WITH_COMMAS, "1,234,567.89"),
        (1234567.89, FluentNumberFormat.WITH_SPACES, "1 234 567.89"),
        (1234.56, FluentNumberFormat.CURRENCY_USD, "$1234.56"),
        (1234.56, FluentNumberFormat.CURRENCY_EUR, "€1234.56"),
        (1234.56, FluentNumberFormat.CURRENCY_GBP, "£1234.56"),
        (0, FluentNumberFormat.DECIMAL_TWO, "0.00"),
        (-123.45, FluentNumberFormat.DECIMAL_TWO, "-123.45"),
    ])
    def test_format_number(self, qapp, input_number: NumericValue, format_str: str, expected_output: str):
        """Test format_number method."""
        formatter = FluentFormatter(locale=QLocale(QLocale.Language.English, QLocale.Country.UnitedStates)) # Use US locale for comma/space
        result = formatter.format_number(input_number, format_str)
        assert result == expected_output

    @pytest.mark.parametrize("size_bytes, expected_output", [
        (500, "500 B"),
        (1023, "1023 B"),
        (1024, "1.0 KB"),
        (1500, "1.5 KB"),
        (1024 * 1024 - 1, "1023.9 KB"),
        (1024 * 1024, "1.0 MB"),
        (1.5 * 1024 * 1024, "1.5 MB"),
        (1024 * 1024 * 1024 - 1, "1023.99 MB"), # Rounds to 2 decimal places
        (1024 * 1024 * 1024, "1.00 GB"),
        (2.75 * 1024 * 1024 * 1024, "2.75 GB"),
        (1024 * 1024 * 1024 * 1024 - 1, "1023.99 GB"), # Rounds to 2 decimal places
        (1024 * 1024 * 1024 * 1024, "1.00 TB"),
        (5.123 * 1024 * 1024 * 1024 * 1024, "5.12 TB"), # Rounds to 2 decimal places
        (0, "0 B"),
    ])
    def test_format_filesize(self, qapp, size_bytes: int, expected_output: str):
        """Test format_filesize method."""
        formatter = FluentFormatter()
        result = formatter.format_filesize(size_bytes)
        assert result == expected_output

    @pytest.mark.parametrize("phone_number, country_code, expected_output", [
        ("1234567890", "US", "(123) 456-7890"),
        ("123-456-7890", "US", "(123) 456-7890"), # Already formatted
        ("(123) 456-7890", "US", "(123) 456-7890"), # Already formatted with symbols
        ("123.456.7890", "US", "(123) 456-7890"), # With dots
        ("123456789", "US", "123456789"), # Too short
        ("12345678901", "US", "12345678901"), # Too long
        ("02071234567", "GB", "02071234567"), # Non-US, should return cleaned digits
        ("+44 20 7123 4567", "GB", "442071234567"), # Non-US with symbols
        ("12345", "CA", "12345"), # Non-US, short
        ("", "US", ""), # Empty string
        (None, "US", ""), # None input (re.sub handles this)
    ])
    def test_format_phone(self, qapp, phone_number: str | None, country_code: str, expected_output: str):
        """Test format_phone method."""
        formatter = FluentFormatter()
        # Handle None input explicitly as re.sub might raise TypeError
        input_phone = phone_number if phone_number is not None else ""
        result = formatter.format_phone(input_phone, country_code)
        assert result == expected_output