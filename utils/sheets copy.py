import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import GOOGLE_SHEET_NAME, GOOGLE_CREDS_JSON
from datetime import datetime, timedelta

COLUMN_MAP = {
    "telegram": "A",
    "name": "B",
    "date": "C",
    "direction": "D",
    "checkin_time": "E",
    "checkout_time": "F",
    "photo_checkin": "G",
    "photo_checkout": "H",
}

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDS_JSON, scope)
client = gspread.authorize(creds)
sheet = client.open(GOOGLE_SHEET_NAME).sheet1

def find_row_by_user_and_date(username, date_str):
    link = f"https://t.me/{username}"
    data = sheet.get_all_values()
    for idx, row in enumerate(data[1:], start=2):
        if row[0] == link and row[2] == date_str:
            return idx
    return None

def find_nearest_checkin_row(username, checkout_time):
    link = f"https://t.me/{username}"
    data = sheet.get_all_values()
    min_diff = timedelta(days=9999)
    nearest_idx = None
    checkout_dt = datetime.strptime(checkout_time, "%Y-%m-%d %H:%M:%S")

    for idx, row in enumerate(data[1:], start=2):
        if len(row) < 8:
            continue
        if row[0] == link:
            checkin_time = row[4]
            checkout_cell = row[5]
            if checkin_time and not checkout_cell:
                try:
                    checkin_dt = datetime.strptime(f"{row[2]} {checkin_time}", "%Y-%m-%d %H:%M")
                    diff = abs((checkout_dt - checkin_dt).total_seconds())
                    if diff < min_diff.total_seconds():
                        min_diff = timedelta(seconds=diff)
                        nearest_idx = idx
                except Exception:
                    continue
    return nearest_idx

def write_checkin(user_id, username, name, direction, time, photo_file_id):
    date_str = datetime.now().strftime("%Y-%m-%d")
    photo_hyperlink = f'=HYPERLINK("{photo_file_id}", "ссылка")'
    tg_link = f"https://t.me/{username}"
    sheet.append_row([
        tg_link, name, date_str, direction, time, "", photo_hyperlink, ""
    ], value_input_option='USER_ENTERED')

def write_checkout(username, time, photo_file_id):
    now = datetime.now()
    checkout_time = now.strftime("%Y-%m-%d %H:%M:%S")
    photo_hyperlink = f'=HYPERLINK("{photo_file_id}", "ссылка")'
    row = find_nearest_checkin_row(username, checkout_time)
    if row:
        sheet.update(f"{COLUMN_MAP['checkout_time']}{row}", [[time]])
        sheet.update(f"{COLUMN_MAP['photo_checkout']}{row}", [[photo_hyperlink]], value_input_option='USER_ENTERED')
    else:
        print(f"❌ Строка не найдена для {username} для чек-аута")

def mark_incomplete_shift(username):
    date_str = datetime.now().strftime("%Y-%m-%d")
    row = find_row_by_user_and_date(username, date_str)
    if row:
        sheet.update(f"{COLUMN_MAP['checkout_time']}{row}", [["Не завершил смену"]])
        sheet.update(f"{COLUMN_MAP['photo_checkout']}{row}", [["—"]])
        print(f"🟡 Отметка 'Не завершил смену' записана для {username}")