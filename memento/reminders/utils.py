from datetime import datetime, timezone
from typing import Optional

from AppKit import NSColor  # noqa: F401
from EventKit import EKReminder, EKCalendar  # noqa: F401
from Foundation import NSDate, NSCalendar  # noqa: F401

from memento.reminders.models import Reminder, Calendar


def datetime_from_ns_date(ns_date: Optional[NSDate]) -> Optional[datetime]:
    """Convert NSDate to Python datetime.

    Args:
        ns_date (NSDate): The NSDate object to convert.

    Returns:
        datetime: The converted datetime object in UTC, or None if conversion fails.
    """
    if ns_date is None:
        return None
    try:
        timestamp = ns_date.timeIntervalSince1970()
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)
    except:
        return None


def hex_to_ns_color(color: Optional[str]) -> Optional[NSColor]:
    """Convert hex color string to NSColor.

    Args:
        color: The hex color string, e.g., '#FF5733'.

    Returns:
        The corresponding NSColor object, or None if conversion fails.
    """
    if color is None:
        return None
    try:
        if color.startswith('#'):
            # Convert hex to RGB
            color = color.lstrip('#')
            r = int(color[0:2], 16) / 255.0
            g = int(color[2:4], 16) / 255.0
            b = int(color[4:6], 16) / 255.0
            return NSColor.colorWithRed_green_blue_alpha_(r, g, b, 1.0)
    except:
        pass  # Color setting failed, continue without it
    return None


def rgba_to_rgb(rgba: Optional[str]) -> Optional[str]:
    """Convert RGBA string to standard hex RGB format.

    Args:
        rgba: The RGBA color string, e.g., '#FF5733FF' or '#FF5733'.

    Returns:
        The RGB color string in hex format, e.g., '#FF5733', or None if input is invalid.
    """
    if not rgba:
        return None

    # Remove # if present
    color = rgba.lstrip('#')

    # Handle RGBA format (8 chars) - strip alpha channel
    if len(color) == 8:
        return f"#{color[:6].upper()}"
    # Handle RGB format (6 chars)
    elif len(color) == 6:
        return f"#{color.upper()}"

    return None


def reminder_from_ek(ek_reminder: EKReminder) -> Reminder:
    """Convert EKReminder to Reminder dataclass.

    Args:
        ek_reminder: The EKReminder object to convert.

    Returns:
        The converted Reminder object.
    """
    due_date = None
    if hasattr(ek_reminder,
               'dueDateComponents') and ek_reminder.dueDateComponents():
        components = ek_reminder.dueDateComponents()
        try:
            year = components.year() if hasattr(components,
                                                'year') and components.year() > 0 else 1970
            month = components.month() if hasattr(components,
                                                  'month') and components.month() > 0 else 1
            day = components.day() if hasattr(components,
                                              'day') and components.day() > 0 else 1
            hour = components.hour() if hasattr(components,
                                                'hour') and components.hour() >= 0 else 0
            minute = components.minute() if hasattr(components,
                                                    'minute') and components.minute() >= 0 else 0
            due_date = datetime(year, month, day, hour, minute,
                                tzinfo=timezone.utc)
        except:
            try:
                calendar = NSCalendar.currentCalendar()
                ns_date = calendar.dateFromComponents_(components)
                if ns_date:
                    due_date = datetime_from_ns_date(ns_date)
            except:
                due_date = None

    return Reminder(
        id=ek_reminder.calendarItemIdentifier(),
        title=ek_reminder.title() or "",
        notes=ek_reminder.notes() or "",
        completed=ek_reminder.isCompleted(),
        creation_date=datetime_from_ns_date(ek_reminder.creationDate()),
        completion_date=datetime_from_ns_date(
            ek_reminder.completionDate()) if ek_reminder.completionDate() else None,
        due_date=due_date,
        priority=ek_reminder.priority(),
        calendar=ek_reminder.calendar().title() if ek_reminder.calendar() else None,
        url=str(ek_reminder.URL()) if ek_reminder.URL() else None
    )


def calendar_from_ek(ek_calendar: EKCalendar) -> Calendar:
    """Convert EKCalendar to Calendar dataclass.

    Args:
        ek_calendar: The EKCalendar object to convert.

    Returns:
        The converted Calendar object.
    """
    color = rgba_to_rgb(
        getattr(ek_calendar, 'colorString', lambda: None)() or
        getattr(ek_calendar, 'colorStringRaw', lambda: None)()
    )
    return Calendar(
        id=ek_calendar.calendarIdentifier(),
        title=ek_calendar.title(),
        color=color,
        allows_modifications=ek_calendar.allowsContentModifications(),
        is_subscribed=ek_calendar.isSubscribed()
    )
