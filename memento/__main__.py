import dotenv

from memento.engine import run


def main():
    # Load environment variables from .env file
    dotenv.load_dotenv()
    # Run the Memento engine
    run()


if __name__ == "__main__":
    main()
