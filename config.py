import logging
import os

from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

# Читаем токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Отсутствует BOT_TOKEN в .env файле!")

# Настройки логгера
LOG_FILE = os.path.join("bot.log")

logging.basicConfig(
    level=logging.INFO,  # Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s [%(levelname)s] %(message)s",  # Формат логов
    datefmt="%Y-%m-%d %H:%M:%S",  # Формат даты
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),  # Лог в файл
        logging.StreamHandler(),  # Лог в консоль
    ],
)

logger = logging.getLogger("bot_log")

GOOGLE_JSON, GOOGLE_SHEET_NAME = 'google_keys.json', os.getenv('GOOGLE_DOC_NAME')
