from config import logger  # Если используешь логирование
from database import Database
from utils import get_downtime, clean_old_history


def job():
    db = Database()
    chats = db.fetchall("SELECT id FROM chats")
    clean_old_history()
    downtime_data = {}
    for chat_id, in chats:
        result = get_downtime(chat_id)
        downtime_data.update(result)

    logger.info(f"Downtime data received")


# Запускаем каждые 10 минут
# schedule.every(60).minutes.do(job)

if __name__ == "__main__":
    job()
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
