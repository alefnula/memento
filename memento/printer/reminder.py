import os
from typing import Optional

from escpos.printer import Network

from memento.printer import utils


def print_reminder(
        title: str,
        text: Optional[str] = None,
        link: Optional[str] = None,
        assignee: Optional[str] = None,
):
    """Print a reminder.

    Args:
        title: The title of the reminder
        text: The body text of the reminder
        link: Any URL or link associated with the reminder
        assignee: The name of the person assigned to the reminder
    """
    p = Network(
        host=os.environ.get("PRINTER_HOST"),
        profile=os.environ.get("PRINTER_PROFILE"),
    )
    # Print the title
    utils.print_title(p, title)
    # Print the body text if provided
    if text is not None:
        utils.print_body(p, text)
    # Print the link if provided
    if link is not None:
        utils.print_link(p, link)
    # Print the assignee name if provided
    if assignee is not None:
        utils.print_assignee(p, assignee)
    # Cut the paper
    p.cut()
