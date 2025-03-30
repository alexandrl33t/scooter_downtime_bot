from config import logger, GOOGLE_JSON, GOOGLE_SHEET_NAME
from database import Database
from google_sheets import update_google_sheet
from utils import get_downtime, clean_old_history


def job():
    db = Database()
    chats = db.fetchall("SELECT id FROM chats")
    clean_old_history()
    downtime_data = {}
    for chat_id, in chats:
        result = get_downtime(chat_id)
        downtime_data.update(result)
        update_google_sheet(downtime_data, GOOGLE_JSON, GOOGLE_SHEET_NAME)
    logger.info(f"Downtime data received")


# Запускаем каждые 10 минут
# schedule.every(60).minutes.do(job)

if __name__ == "__main__":
    job()
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
