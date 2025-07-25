import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")

# Интервалы в часах, настраиваются через .env
REMINDER_INTERVAL_HOURS = int(os.getenv("REMINDER_INTERVAL_HOURS", 0.05))  # Через сколько часов напоминать о чек-ауте
INCOMPLETE_INTERVAL_HOURS = int(os.getenv("INCOMPLETE_INTERVAL_HOURS", 24))  # Через сколько часов смена считается незавершённой
CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", 3600))
IMAGES_DIR = os.getenv("IMAGES_DIR")
BASE_URL = os.getenv("BASE_URL")