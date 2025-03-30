import functools

import telebot
from telebot.types import Message

from config import BOT_TOKEN, logger
from database import Database
from utils import insert_chat, parse_parking_data, insert_parking_data

logger.info("Инициализируем бота")
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

db = Database()
# Инициализация БД
db.init_db()


def ensure_chat_exists(handler):
    """Декоратор, который проверяет наличие чата в БД и добавляет его, если нужно"""

    @functools.wraps(handler)
    def wrapper(message: Message, *args, **kwargs):
        chat_id = message.chat.id
        chat_name = message.chat.title
        message_id = message.message_id

        insert_chat(chat_id, chat_name, message_id)

        return handler(message, *args, **kwargs)

    return wrapper


@bot.edited_message_handler(func=lambda m: True)
@ensure_chat_exists
def edited_message_handler(message: Message):
    """Обработчик редактированных сообщений"""
    chat_id = message.chat.id
    logger.info(f"Edited message from {chat_id}")
    parking_data = parse_parking_data(message.text)
    insert_parking_data(message.message_id, parking_data)
    logger.info("Got parking data")


logger.info("Запускаем бота...")
bot.infinity_polling()
