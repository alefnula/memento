import time
from datetime import datetime
from typing import Optional

from EventKit import (
    EKReminder,
    EKCalendar,
    EKEventStore,
    EKEntityTypeReminder,
    EKSourceTypeLocal,
    EKSourceTypeCalDAV,
)
from Foundation import NSDate, NSDateComponents  # noqa: F401

from memento.reminders.models import Calendar, Reminder
from memento.reminders.utils import hex_to_ns_color, reminder_from_ek, \
    calendar_from_ek


class PyObjCRemindersError(Exception):
    """Custom exception for PyObjC Reminders errors"""
    pass


class Reminders:
    """Direct PyObjC-based CRUD interface for Mac Reminders."""

    def __init__(self):
        """Initialize the EventKit store and request permissions."""
        self.event_store = EKEventStore.alloc().init()
        self.access_granted = False
        self._request_access()

    def _request_access(self):
        """Request access to reminders."""
        completion_called = [False]

        def completion_handler(granted, error):
            self.access_granted = granted
            completion_called[0] = True

        try:
            self.event_store.requestFullAccessToRemindersWithCompletion_(
                completion_handler)
        except AttributeError:
            try:
                self.event_store.requestAccessToEntityType_completion_(
                    EKEntityTypeReminder, completion_handler
                )
            except AttributeError:
                self.event_store.requestAccess_completion_(
                    EKEntityTypeReminder, completion_handler
                )

        # Wait for completion
        start_time = time.time()
        while not completion_called[0] and time.time() - start_time < 10:
            time.sleep(0.1)

        if not self.access_granted:
            raise PyObjCRemindersError("Access to reminders was denied")

    def _ensure_access(self):
        """Ensure we have access to reminders."""
        if not self.access_granted:
            raise PyObjCRemindersError("No access to reminders")

    def create_reminder(
            self, title: str,
            notes: str = "",
            due_date: Optional[datetime] = None,
            priority: int = 0,
            calendar: Optional[str] = None
    ) -> Reminder:
        """Create a new reminder.

        Args:
            title: The title of the reminder.
            notes: Additional notes for the reminder.
            due_date: The due date for the reminder.
            priority: The priority of the reminder (0-9).
            calendar: The calendar to add the reminder to.

        Returns:
            The created reminder object.
        """
        self._ensure_access()

        reminder = EKReminder.reminderWithEventStore_(self.event_store)
        reminder.setTitle_(title)

        if notes:
            reminder.setNotes_(notes)

        reminder.setPriority_(priority)

        if due_date:
            components = NSDateComponents.alloc().init()
            components.setYear_(due_date.year)
            components.setMonth_(due_date.month)
            components.setDay_(due_date.day)
            components.setHour_(due_date.hour)
            components.setMinute_(due_date.minute)
            reminder.setDueDateComponents_(components)

        # Set calendar
        if calendar:
            calendars = self.event_store.calendarsForEntityType_(
                EKEntityTypeReminder)
            target_calendar = None
            for cal in calendars:
                if cal.title() == calendar:
                    target_calendar = cal
                    break
            reminder.setCalendar_(
                target_calendar or self.event_store.defaultCalendarForNewReminders())
        else:
            reminder.setCalendar_(
                self.event_store.defaultCalendarForNewReminders())

        error = self.event_store.saveReminder_commit_error_(reminder, True,
                                                            None)
        if error[1]:
            raise PyObjCRemindersError(f"Failed to create reminder: {error[1]}")

        return reminder_from_ek(reminder)

    def get_reminders(
            self,
            include_completed: bool = False,
            calendar: Optional[str] = None
    ) -> list[Reminder]:
        """Get all reminders.

        Args:
            include_completed: Whether to include completed reminders.
            calendar: The calendar to filter reminders by (optional).

        Returns:
            A list of reminders.
        """
        self._ensure_access()

        if calendar:
            calendars = self.event_store.calendarsForEntityType_(
                EKEntityTypeReminder)
            target_calendars = [cal for cal in calendars if
                                cal.title() == calendar]
            if not target_calendars:
                return []
        else:
            target_calendars = self.event_store.calendarsForEntityType_(
                EKEntityTypeReminder)

        predicate = self.event_store.predicateForRemindersInCalendars_(
            target_calendars)

        all_reminders = []
        completion_called = [False]

        def completion_handler(reminders):
            if reminders:
                all_reminders.extend(reminders)
            completion_called[0] = True

        self.event_store.fetchRemindersMatchingPredicate_completion_(predicate,
                                                                     completion_handler)

        start_time = time.time()
        while not completion_called[0] and time.time() - start_time < 10:
            time.sleep(0.1)

        if not completion_called[0]:
            raise PyObjCRemindersError("Timeout fetching reminders")

        result = []
        for reminder in all_reminders:
            if include_completed or not reminder.isCompleted():
                result.append(reminder_from_ek(reminder))

        return result

    def get_reminder(self, id: str) -> Optional[Reminder]:
        """Get a specific reminder by its ID.

        Args:
            id: The identifier of the reminder to retrieve.

        Returns:
            The reminder object if found, otherwise None.
        """
        self._ensure_access()

        reminder = self.event_store.calendarItemWithIdentifier_(id)
        if reminder and isinstance(reminder, EKReminder):
            return reminder_from_ek(reminder)
        return None

    def update_reminder(
            self,
            id: str,
            title: Optional[str] = None,
            notes: Optional[str] = None,
            calendar: Optional[str] = None,
            completed: Optional[bool] = None,
            due_date: Optional[datetime] = None,
            priority: Optional[int] = None
    ) -> Reminder:
        """Update a reminder.

        Args:
            id: The identifier of the reminder to update.
            title: The new title for the reminder.
            notes: The new notes for the reminder.
            calendar: The new calendar for the reminder..
            completed: Whether the reminder is completed.
            due_date: The new due date for the reminder.
            priority: The new priority for the reminder (0-9).

        Returns:
            The updated reminder object.
        """
        self._ensure_access()

        reminder = self.event_store.calendarItemWithIdentifier_(id)
        if not reminder or not isinstance(reminder, EKReminder):
            raise PyObjCRemindersError(f"Reminder not found: {id}")

        if title is not None:
            reminder.setTitle_(title)

        if notes is not None:
            reminder.setNotes_(notes)

        if calendar is not None:
            calendars = self.event_store.calendarsForEntityType_(
                EKEntityTypeReminder
            )
            target_calendar = None
            for cal in calendars:
                if cal.title() == calendar:
                    target_calendar = cal
                    break
            if target_calendar:
                reminder.setCalendar_(target_calendar)
            else:
                raise PyObjCRemindersError(f"Calendar not found: {calendar}")

        if completed is not None:
            reminder.setCompleted_(completed)
            if completed:
                reminder.setCompletionDate_(NSDate.date())
            else:
                reminder.setCompletionDate_(None)

        if priority is not None:
            reminder.setPriority_(priority)

        if due_date is not None:
            components = NSDateComponents.alloc().init()
            components.setYear_(due_date.year)
            components.setMonth_(due_date.month)
            components.setDay_(due_date.day)
            components.setHour_(due_date.hour)
            components.setMinute_(due_date.minute)
            reminder.setDueDateComponents_(components)

        error = self.event_store.saveReminder_commit_error_(reminder, True,
                                                            None)
        if error[1]:
            raise PyObjCRemindersError(f"Failed to update reminder: {error[1]}")

        return reminder_from_ek(reminder)

    def delete_reminder(self, id: str) -> bool:
        """Delete a reminder.

        Args:
            id: The identifier of the reminder to delete.

        Returns:
            True if the reminder was deleted successfully, False otherwise.
        """
        self._ensure_access()

        reminder = self.event_store.calendarItemWithIdentifier_(id)
        if not reminder or not isinstance(reminder, EKReminder):
            return False

        error = self.event_store.removeReminder_commit_error_(reminder, True,
                                                              None)
        return error[1] is None

    def create_calendar(self, title: str,
                        color: Optional[str] = None) -> Calendar:
        """Create a new calendar.

        Args:
            title: The title of the calendar.
            color: The color of the calendar in hex format (e.g., "#FF5733").

        Returns:
            The created calendar object.
        """
        self._ensure_access()

        calendar = EKCalendar.calendarForEntityType_eventStore_(
            EKEntityTypeReminder, self.event_store
        )
        calendar.setTitle_(title)

        ns_color = hex_to_ns_color(color)
        if ns_color:
            calendar.setColor_(ns_color)

        # Set source to local
        sources = self.event_store.sources()
        target_source = None
        # Look for iCloud source first (most common)
        for source in sources:
            if (
                    source.sourceType() == EKSourceTypeCalDAV and
                    source.title() == "iCloud"
            ):
                target_source = source
                break

        # If no iCloud, use any CalDAV source
        if not target_source:
            for source in sources:
                if source.sourceType() == EKSourceTypeCalDAV:
                    target_source = source
                    break

        # Last resort: use first available source
        if not target_source and sources:
            target_source = sources[0]

        if not target_source:
            raise PyObjCRemindersError("No calendar sources available")

        calendar.setSource_(target_source)

        error = self.event_store.saveCalendar_commit_error_(calendar, True,
                                                            None)
        if error[1]:
            raise PyObjCRemindersError(f"Failed to create calendar: {error[1]}")

        return calendar_from_ek(calendar)

    def get_calendars(self) -> list[Calendar]:
        """Get all reminder calendars.

        Returns:
            A list of all reminder calendars.
        """
        self._ensure_access()

        calendars = self.event_store.calendarsForEntityType_(
            EKEntityTypeReminder)
        result = []

        for calendar in calendars:
            result.append(calendar_from_ek(calendar))

        return result

    def get_calendar(self, id: str) -> Optional[Calendar]:
        """Get a specific calendar by its ID.

        Args:
            id: The identifier of the calendar to retrieve.

        Returns:
            The calendar object if found, otherwise None.
        """
        self._ensure_access()

        calendars = self.event_store.calendarsForEntityType_(
            EKEntityTypeReminder)
        for calendar in calendars:
            if calendar.calendarIdentifier() == id:
                return calendar_from_ek(calendar)
        return None

    def get_calendar_by_title(self, title: str) -> Optional[Calendar]:
        """Get a calendar by its title.

        Args:
            title: The title of the calendar to retrieve.

        Returns:
            The calendar object if found, otherwise None.
        """
        self._ensure_access()

        calendars = self.event_store.calendarsForEntityType_(
            EKEntityTypeReminder)
        for calendar in calendars:
            if calendar.title() == title:
                return calendar_from_ek(calendar)
        return None

    def update_calendar(
            self,
            id: str,
            title: Optional[str] = None,
            color: Optional[str] = None
    ) -> Calendar:
        """Update a calendar."""
        self._ensure_access()

        calendars = self.event_store.calendarsForEntityType_(
            EKEntityTypeReminder)
        target_calendar = None

        for calendar in calendars:
            if calendar.calendarIdentifier() == id:
                target_calendar = calendar
                break

        if not target_calendar:
            raise PyObjCRemindersError(f"Calendar not found: {id}")

        if not target_calendar.allowsContentModifications():
            raise PyObjCRemindersError("Calendar does not allow modifications")

        if title is not None:
            target_calendar.setTitle_(title)

        ns_color = hex_to_ns_color(color)
        if ns_color:
            target_calendar.setColor_(ns_color)

        error = self.event_store.saveCalendar_commit_error_(target_calendar,
                                                            True, None)
        if error[1]:
            raise PyObjCRemindersError(f"Failed to update calendar: {error[1]}")

        return calendar_from_ek(target_calendar)

    def delete_calendar(self, id: str) -> bool:
        """Delete a calendar.

        Args:
            id: The identifier of the calendar to delete.

        Returns:
            True if the calendar was deleted successfully, False otherwise.
        """
        self._ensure_access()

        calendars = self.event_store.calendarsForEntityType_(
            EKEntityTypeReminder)
        target_calendar = None

        for calendar in calendars:
            if calendar.calendarIdentifier() == id:
                target_calendar = calendar
                break

        if not target_calendar:
            return False

        if not target_calendar.allowsContentModifications():
            raise PyObjCRemindersError("Calendar does not allow modifications")

        error = self.event_store.removeCalendar_commit_error_(target_calendar,
                                                              True, None)
        return error[1] is None
