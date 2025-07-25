import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import GOOGLE_SHEET_NAME, GOOGLE_CREDS_JSON
from datetime import datetime, timedelta

# Авторизация
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDS_JSON, scope)
client = gspread.authorize(creds)
sheet = client.open(GOOGLE_SHEET_NAME).sheet1

# Поиск строки по Telegram username (в формате ссылки) и дате
def find_row_by_user_and_date(username, date_str):
    link = f"https://t.me/{username}"
    data = sheet.get_all_records()
    for idx, row in enumerate(data, start=2):  # С учётом заголовка
        if row["Telegram тег"] == link and row["Дата смены"] == date_str:
            return idx
    return None

# Поиск самой близкой строки чек-ина без чек-аута для пользователя (по времени)
def find_nearest_checkin_row(username, checkout_time):
    link = f"https://t.me/{username}"
    data = sheet.get_all_records()
    min_diff = timedelta(days=9999)
    nearest_idx = None
    checkout_dt = datetime.strptime(checkout_time, "%Y-%m-%d %H:%M:%S")
    for idx, row in enumerate(data, start=2):
        if row["Telegram тег"] == link:
            checkin_time = row.get("Время начала работы")
            checkout_cell = row.get("Время завершения работы")
            if checkin_time and (not checkout_cell or checkout_cell == ""):
                try:
                    checkin_dt = datetime.strptime(row["Дата смены"] + " " + checkin_time, "%Y-%m-%d %H:%M")
                except Exception:
                    continue
                diff = abs((checkout_dt - checkin_dt).total_seconds())
                if diff < min_diff.total_seconds():
                    min_diff = timedelta(seconds=diff)
                    nearest_idx = idx
    return nearest_idx

# Чек-ин: создаём новую строку с пустыми полями для чек-аута
def write_checkin(user_id, username, name, direction, time, photo_file_id):
    date_str = datetime.now().strftime("%Y-%m-%d")
    tg_link = f"https://t.me/{username}"
    sheet.append_row([
        tg_link, name, date_str, direction, time, "", photo_file_id, ""
    ])

# Чек-аут: ищем ближайший чек-ин без чек-аута и записываем туда
def write_checkout(username, time, photo_file_id):
    now = datetime.now()
    checkout_time = now.strftime("%Y-%m-%d %H:%M:%S")
    row = find_nearest_checkin_row(username, checkout_time)
    if row:
        sheet.update(f"F{row}", [[time]])          # ВРЕМЯ ЗАВЕРШЕНИЯ РАБОТЫ
        sheet.update(f"H{row}", [[photo_file_id]]) # ФОТОГРАФИЯ КОНЦА РАБОТЫ
    else:
        print(f"❌ Строка не найдена для {username} для чек-аута (поиск ближайшей)")

def mark_incomplete_shift(username):
    from datetime import datetime
    date_str = datetime.now().strftime("%Y-%m-%d")
    row = find_row_by_user_and_date(username, date_str)
    if row:
        sheet.update(f"F{row}", [["Не завершил смену"]])  # Время завершения
        sheet.update(f"H{row}", [["—"]])                 # Фото чек-аута
        print(f"🟡 Отметка 'Не завершил смену' записана для {username}")