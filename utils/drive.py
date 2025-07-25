from aiogram import Bot
from aiogram.types import File
import aiofiles
import os
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from aiogram.filters import Command

SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'
FOLDER_ID = '13cbU5Na94M64S0RY6Trz4-_8e7S3FXZu'  # ID вашей папки

# Авторизация через OAuth2 пользователя (тестовый аккаунт)
def auth_drive_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

async def download_photo(bot: Bot, file_id: str, local_path: str):
    file: File = await bot.get_file(file_id)
    file_path = file.file_path
    content = await bot.download_file(file_path)
    async with aiofiles.open(local_path, "wb") as f:
        await f.write(content.read())

def upload_to_drive(local_path: str, new_filename: str) -> str:
    service = auth_drive_service()
    file_metadata = {
        'name': new_filename,
        'parents': [FOLDER_ID],
    }
    media = MediaFileUpload(local_path, mimetype='image/jpeg')
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()
    service.permissions().create(
        fileId=file['id'],
        body={'role': 'reader', 'type': 'anyone'}
    ).execute()
    return file['webViewLink']

async def save_volunteer_photo(bot, file_id: str, name: str, is_checkin: bool) -> str:
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    label = "Чек-ин" if is_checkin else "Чек-аут"
    filename = f"{name}_{date_str}_{label}.jpg".replace(" ", "_")
    local_path = f"temp_{filename}"
    try:
        await download_photo(bot, file_id, local_path)
        drive_link = upload_to_drive(local_path, filename)
        return drive_link
    except Exception as e:
        print(f"⚠️ Ошибка при обработке фото: {e}")
        return ""
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)