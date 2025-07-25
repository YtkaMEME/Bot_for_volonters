# Bot for Volunteers

Телеграм-бот для учёта волонтёров с поддержкой Google Sheets, Google Drive, FSM (aiogram 3), асинхронной работы и напоминаний.

## Возможности
- Чек-ин/чек-аут с фото
- Сохранение данных в Google Sheets
- Загрузка фотографий на Google Drive
- FSM для изоляции состояний пользователей
- Асинхронная работа (aiogram + aiosqlite)
- Напоминания о незавершённых сменах
- Готов к работе с сотнями пользователей одновременно

## Быстрый старт

### 1. Клонируйте репозиторий
```bash
git clone <your-repo-url>
cd Bot_for_volunteers
```

### 2. Создайте и активируйте виртуальное окружение
```bash
python3 -m venv env
source env/bin/activate
```

### 3. Установите зависимости
```bash
pip install -r requirements.txt
```

### 4. Настройте переменные окружения
Создайте файл `.env` в корне проекта:
```
BOT_TOKEN=your_telegram_bot_token
GOOGLE_SHEET_NAME=Название_вашего_гугл_шита
GOOGLE_CREDS_JSON=creds.json
REMINDER_INTERVAL_HOURS=15
INCOMPLETE_INTERVAL_HOURS=24
CHECK_INTERVAL_SECONDS=60
```
- `REMINDER_INTERVAL_HOURS` — через сколько часов после чек-ина напоминать о чек-ауте
- `INCOMPLETE_INTERVAL_HOURS` — через сколько часов смена считается незавершённой
- `CHECK_INTERVAL_SECONDS` — как часто проверять состояния (в секундах)

### 5. Добавьте Google credentials
- Получите сервисный ключ Google API и сохраните как `creds.json` в корне проекта.
- Дайте сервисному аккаунту доступ к вашему Google Sheet и Google Drive.

### 6. Запустите бота
```bash
python bot.py
```

## Рекомендации для продакшена
- Для большого количества пользователей используйте RedisStorage вместо MemoryStorage (FSM).
- Не храните секреты (`creds.json`, `token.json`, `.env`) в публичном репозитории.
- Используйте supervisor/systemd для автозапуска бота на сервере.
- Для деплоя на сервере убедитесь, что установлены Python 3.9+, Redis (если нужен), все зависимости.

## Структура проекта
- `bot.py` — точка входа
- `handlers/` — обработчики сообщений и команд
- `utils/` — вспомогательные модули (работа с БД, Google API, FSM)
- `keyboards/` — inline-клавиатуры
- `data/` — база данных пользователей (sqlite)

## Лицензия
MIT (или ваша лицензия) 