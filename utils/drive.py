from aiogram import Bot
from aiogram.types import File
import aiofiles
import os
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime
from PIL import Image
from config import IMAGES_DIR
from config import BASE_URL

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



os.makedirs(IMAGES_DIR, exist_ok=True)

async def save_volunteer_photo(bot: Bot, file_id: str, name: str, is_checkin: bool) -> str:
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H-%M")
    label = "checkin" if is_checkin else "checkout"
    filename = f"{name}_{date_str}_{time_str}_{label}.jpg".replace(" ", "_")
    local_path = os.path.join(IMAGES_DIR, filename)

    # Скачиваем фото
    file: File = await bot.get_file(file_id)
    file_path = file.file_path
    content = await bot.download_file(file_path)
    temp_path = f"temp_{filename}"
    async with aiofiles.open(temp_path, "wb") as f:
        await f.write(content.read())

    # Сжимаем фото и сохраняем в images/
    try:
        with Image.open(temp_path) as img:
            img = img.convert("RGB")
            img.save(local_path, "JPEG", quality=70, optimize=True)  # quality=70 — компромисс между размером и качеством
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    # Возвращаем публичную ссылку
    return f"{BASE_URL}/{filename}"