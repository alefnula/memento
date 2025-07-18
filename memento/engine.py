import os

from memento.llm import LLMProcessor
from memento.printer import print_reminder
from memento.reminders import Reminders

PROCESSED_CALENDAR = "Processed"


def run():
    """Run the Memento engine to process reminders and print them."""
    reminders = Reminders()
    processor = LLMProcessor()
    skip_calendars = os.environ.get("SKIP_CALENDARS", "").split(",")

    processed_calendar = reminders.get_calendar_by_title(PROCESSED_CALENDAR)
    if processed_calendar is None:
        reminders.create_calendar(PROCESSED_CALENDAR)

    for reminder in reminders.get_reminders():
        if (
                reminder.calendar != PROCESSED_CALENDAR and
                reminder.calendar not in skip_calendars
        ):
            processed = processor.process_reminder(reminder.text)
            print_reminder(
                title=reminder.title,
                text=processed.text,
                link=processed.link,
                assignee=processed.assignee,
            )
            reminders.update_reminder(
                id=reminder.id,
                calendar=PROCESSED_CALENDAR,
            )
