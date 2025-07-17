from textwrap import wrap

import textcase
from escpos.printer import Network


def print_title(
    p: Network,
    text: str,
    max_width: int = 20,
    font_width: int = 2,
    font_height: int = 2
):
    """Print a title with borders, splitting text across multiple lines.

    Args:
        p: ESC/POS printer object
        text: The title text to print
        max_width: Maximum characters per line (default 20)
        font_width: Width multiplier for the text (default 2)
        font_height: Height multiplier for the text (default 2)
    """
    # Split title into words
    lines = wrap(
        textcase.title(
            text,
            boundaries=[textcase.SPACE],
            strip_punctuation=False
        ),
        width=max_width,
    )

    # Set text size and alignment
    p.set(
        align='center',
        custom_size=True,
        width=font_width,
        height=font_height
    )

    # Top border
    p.text(f"┌─{'─' * max_width}─┐\n")

    for line in lines:
        p.text(f"│ {line.center(max_width)} │\n")

    # Bottom border
    p.text(f"└─{'─' * max_width}─┘\n\n")

    # Reset to normal text size
    p.set(align="left", normal_textsize=True)

def print_body(
    p: Network,
    text: str,
    max_width: int = 22,
    font_width: int = 2,
    font_height: int = 1
):
    """Print a body section splitting title across multiple lines.

    Args:
        p: ESC/POS printer object
        text: The text to print
        max_width: Maximum characters per line (default 22)
        font_width: Width multiplier for the text (default 2)
        font_height: Height multiplier for the text (default 1)
    """
    # Split title into words
    lines = wrap(
        textcase.title(
            text,
            boundaries=[textcase.SPACE],
            strip_punctuation=False
        ),
        width=max_width,
    )

    # Set text size and alignment
    p.set(
        align='center',
        custom_size=True,
        width=font_width,
        height=font_height
    )

    for line in lines:
        p.text(f"{line.center(max_width)}\n")
    p.text("\n")

    # Reset to normal text size
    p.set(align="left", normal_textsize=True)

def print_assignee(
    p: Network,
    text: str,
    max_width: int = 22,
    font_width: int = 2,
    font_height: int = 1
):
    """Print the assignee name.

    Args:
        p: ESC/POS printer object
        text: The assignee name to print
        max_width: Maximum characters per line (default 22)
        font_width: Width multiplier for the text (default 2)
        font_height: Height multiplier for the text (default 1)
    """
    # Set text size and alignment
    p.set(
        align='right',
        custom_size=True,
        width=font_width,
        height=font_height
    )

    # Print the assignee name
    p.text(f"\n#{text}\n\n")

    # Reset to normal text size
    p.set(align="left", normal_textsize=True)
