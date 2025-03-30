import re
from datetime import datetime, timedelta

from config import logger
from database import Database


def insert_chat(chat_id, chat_name, message_id):
    """Добавляет чат и сообщение в БД (если их нет)"""
    db = Database()  # Создаём объект БД

    # Проверяем, есть ли чат
    existing_chat = db.fetchone("SELECT id FROM chats WHERE id = ?", (chat_id,))
    existing_message_id = db.fetchone("SELECT id FROM message WHERE id = ?", (message_id,))
    if existing_chat and existing_message_id:
        return
    if not existing_chat:
        db.execute("INSERT OR IGNORE INTO chats (id, name) VALUES (?, ?)", (chat_id, chat_name))
        logger.info(f"Добавлен чат с ID: {chat_id}")
    if not existing_message_id:
        # Добавляем сообщение
        db.execute(
            "INSERT OR IGNORE INTO message (id, chat_id, last_update) VALUES (?, ?, datetime('now'))",
            (message_id, chat_id),
        )
        logger.info(f"Добавлено сообщение с ID: {message_id}")


def parse_parking_data(text):
    parking_data = {}

    # Регулярка для поиска парковок с количеством самокатов
    pattern = re.compile(r"(🅿️[\s🌞🌚🛴]+)([\w\s\d.,-]+?)\s*-\s*(\d+)")

    matches = pattern.findall(text)
    for prefix, name, count in matches:
        full_name = f"{prefix.strip()} {name.strip()}"
        parking_data[full_name] = int(count)

    return parking_data


def insert_parking_data(message_id, parking_data):
    """Заполняет таблицы parking и history данными о парковках и самокатах."""
    db = Database()
    for name, scooter_count in parking_data.items():
        # Проверяем, есть ли парковка в базе
        if not db.fetchone("SELECT id FROM parking WHERE name = ? AND message_id = ?", (name, message_id)):
            db.execute(
                "INSERT OR IGNORE INTO parking (name, message_id) VALUES (?, ?)",
                (name, message_id)
            )

        parking_id = db.fetchone("SELECT id FROM parking WHERE name = ? AND message_id = ?", (name, message_id))
        parking_id = parking_id[0]
        # Добавляем запись в историю
        db.execute(
            "INSERT INTO history (parking_id, scooter_count, time_update) VALUES (?, ?, ?)",
            (parking_id, scooter_count, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )


def get_downtime(chat_id):
    db = Database()

    # Получаем название чата по chat_id
    chat = db.fetchone("SELECT name FROM chats WHERE id = ?", (chat_id,))
    if not chat:
        return {}  # Если чата нет в БД, возвращаем пустой словарь

    chat_name = chat[0]  # Извлекаем название чата

    # Получаем все message_id, связанные с этим chat_id
    message = db.fetchone("SELECT id FROM message WHERE chat_id = ?", (chat_id,))
    if not message:
        return {chat_name: {}}  # Если сообщений нет, то и парковок нет

    message_id = message[0]  # Извлекаем message_id

    # Получаем список парковок, относящихся к этому message_id
    parkings = db.fetchall("SELECT id, name FROM parking WHERE message_id = ?", (message_id,))
    if not parkings:
        return {chat_name: {}}  # Если парковок нет, возвращаем пустой словарь

    downtime_result = {}  # Словарь для хранения простоев

    # Получаем сегодняшнюю дату в формате YYYY-MM-DD
    today = datetime.now().strftime("%Y-%m-%d")

    for parking_id, parking_name in parkings:
        downtime_minutes = 0
        # 5️⃣ Достаем историю самокатов для текущей парковки за сегодняшний день
        history = db.fetchall("""
            SELECT scooter_count, time_update 
            FROM history 
            WHERE parking_id = ? AND DATE(time_update) = ? 
            ORDER BY time_update ASC
        """, (parking_id, today))

        if not history:
            downtime_result[parking_name] = int(downtime_minutes)
            continue

        for i in range(len(history) - 1):
            if history[i][0] == 0:  # если скутеров 0 на парковке то начинаем считать минуты от этой даты
                first_time_obj = datetime.strptime(history[i][1], "%Y-%m-%d %H:%M:%S")
                next_time_obj = datetime.strptime(history[i + 1][1], "%Y-%m-%d %H:%M:%S")
                downtime_minutes += (next_time_obj - first_time_obj).total_seconds() // 60

        downtime_result[parking_name] = int(downtime_minutes)

    return {chat_name: downtime_result}


def clean_old_history():
    """Удаляет записи из history, у которых time_update старше 7 дней"""
    db = Database()

    # Определяем дату, старше которой записи удалять
    week_ago = datetime.now() - timedelta(days=7)
    week_ago_str = week_ago.strftime("%Y-%m-%d %H:%M:%S")

    query = "DELETE FROM history WHERE time_update < ?"
    db.execute(query, (week_ago_str,))

    print(f"Удалены записи из history старше {week_ago_str}")
