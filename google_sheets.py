from datetime import datetime

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from config import logger


# Подключение к Google Sheets API
def authorize_gspread(json_keyfile: str, sheet_name: str):
    """Авторизует gspread и возвращает объект Google Sheet"""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
    client = gspread.authorize(creds)
    return client.open(sheet_name)


# Функция обновления данных в Google Sheets
def update_google_sheet(downtime_data: dict, json_keyfile: str, sheet_name: str):
    """
    Обновляет Google Sheet, создавая листы для чатов и записывая простои парковок
    :param downtime_data: {"Название чата": {"Парковка": "Время простоя"}}
    :param json_keyfile: Путь до JSON-файла с ключами сервисного аккаунта
    :param sheet_name: Название Google-таблицы
    """
    # Подключаемся к таблице
    sheet = authorize_gspread(json_keyfile, sheet_name)

    today = datetime.now().strftime("%d-%m-%Y")  # Текущая дата в формате ДД-ММ-ГГГГ
    sum_downtime = 0
    for chat_name, parkings in downtime_data.items():
        try:
            # Пытаемся открыть лист по имени чата
            worksheet = sheet.worksheet(chat_name)
        except gspread.exceptions.WorksheetNotFound:
            # Если листа нет — создаем его
            worksheet = sheet.add_worksheet(title=chat_name, rows=200, cols=90)
            worksheet.update([["Парковка"]], "A1")
            worksheet.update([[today]], "B1")

        existing_parkings = worksheet.col_values(1)

        # Если список парковок пуст, записываем его
        if not existing_parkings:
            parking_list = list(parkings.keys())
            worksheet.update([["Парковка"]] + [[p] for p in parking_list] + [["Общий простой (мин)"]], "A1")
            existing_parkings = ["Парковка"] + parking_list
            # Получаем все заголовки колонок

        # Проверяем, есть ли колонка с сегодняшней датой, иначе создаем
        header_row = worksheet.row_values(1)
        if today not in header_row:
            worksheet.update_cell(1, len(header_row) + 1, today)
            header_row.append(today)

        date_col_idx = header_row.index(today) + 1  # Индекс колонки с датой

        # Заполняем простои по парковкам
        updates = []
        for row_idx, parking_name in enumerate(existing_parkings, start=1):
            if row_idx == 1 or parking_name not in parkings:
                continue  # Пропускаем заголовок и парковки, которых нет в данных

            downtime = parkings[parking_name]
            sum_downtime += downtime
            updates.append({"range": f"{chr(64 + date_col_idx)}{row_idx}", "values": [[downtime]]})

        last_parking_row = len(existing_parkings)

        updates.append({"range": f"{chr(64 + date_col_idx)}{last_parking_row}", "values": [[sum_downtime]]})
        if updates:
            worksheet.batch_update(updates)

    logger.info("Данные успешно обновлены в Google Sheets ✅")
