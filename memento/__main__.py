import os
import dotenv

from memento.printer import print_reminder


def main():
    # Load environment variables from .env file
    dotenv.load_dotenv()

    print_reminder(
        title="Test Reminder",
        text="This is a test reminder to check the printer functionality.",
        assignee="John Doe"
    )


if __name__ == "__main__":
    main()
