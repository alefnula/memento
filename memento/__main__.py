import os
import dotenv


def main():
    # Load environment variables from .env file
    dotenv.load_dotenv()
    print(os.environ.get("PRINTER_HOST"))
    print(os.environ.get("PRINTER_MODEL"))

if __name__ == "__main__":
    main()
