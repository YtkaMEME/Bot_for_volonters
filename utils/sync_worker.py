import asyncio
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from config import GOOGLE_SHEET_NAME, GOOGLE_CREDS_JSON, TIME_SYNC


# Колонки таблицы
COLUMN_ORDER = [
    "telegram",         # A
    "name",             # B
    "date",             # C
    "direction",        # D
    "checkin_time",     # E
    "checkout_time",    # F
    "photo_checkin",    # G
    "photo_checkout",   # H
]

def build_hyperlink(url: str) -> str:
    return f'=HYPERLINK("{url}", "ссылка")' if url else ""

def get_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDS_JSON, scope)
    client = gspread.authorize(creds)
    sheet = client.open(GOOGLE_SHEET_NAME).sheet1
    return sheet

def shift_already_synced(sheet, tg_link, date, checkin_time, checkout_time):
    try:
        all_data = sheet.get_all_values()
        for row in all_data[1:]:
            if len(row) >= 6:
                if (row[0] == tg_link and row[2] == date
                    and row[4] == checkin_time and row[5] == checkout_time):
                    return True
        return False
    except Exception as e:
        print(f"❌ Ошибка при проверке дубля: {e}")
        return False

async def sync_shifts(db):
    sheet = get_google_sheet()

    while True:
        try:
            print("🔍 Проверка несинхронизированных записей...")
            unsynced = await db.get_unsynced_shifts()

            for shift in unsynced:
                row_id = shift[0]
                user_id = shift[1]
                username = shift[2]
                name = shift[3]
                direction = shift[4]
                date = shift[5]
                checkin_time = shift[6]
                checkout_time = shift[7]
                photo_checkin = build_hyperlink(shift[8])
                photo_checkout = build_hyperlink(shift[9])

                tg_link = f"https://t.me/{username}"

                # Пропустить, если нет времени или уже есть такая запись
                if not checkin_time or not checkout_time:
                    print(f"⚠️ Пропущена запись без полного времени: {username} ({date})")
                    continue

                if shift_already_synced(sheet, tg_link, date, checkin_time, checkout_time):
                    print(f"⚠️ Запись уже существует в таблице: {username} ({date}) — пропущена")
                    await db.mark_shift_synced(row_id)
                    continue

                values = [
                    tg_link,
                    name,
                    date,
                    direction,
                    checkin_time,
                    checkout_time,
                    photo_checkin,
                    photo_checkout
                ]

                try:
                    sheet.append_row(values, value_input_option='USER_ENTERED')
                    await db.mark_shift_synced(row_id)
                    print(f"✅ Запись синхронизирована для {username} ({date})")
                except Exception as e:
                    print(f"❌ Ошибка при синхронизации строки {row_id}: {e}")

        except Exception as e:
            print(f"🔥 Критическая ошибка воркера: {e}")

        await asyncio.sleep(60)  # интервал между циклами

# Пример запуска из отдельного процесса
if __name__ == "__main__":
    from utils.db import AsyncDB
    db = AsyncDB("your_database_path.db")  # обнови путь
    asyncio.run(sync_shifts(TIME_SYNC))