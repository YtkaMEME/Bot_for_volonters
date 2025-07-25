from datetime import datetime, timedelta
from utils.sheets import mark_incomplete_shift
from utils.db import AsyncDB
from aiogram import Bot
import asyncio
import logging
from config import REMINDER_INTERVAL_HOURS, INCOMPLETE_INTERVAL_HOURS, CHECK_INTERVAL_SECONDS

async def check_user_states(bot: Bot, db: AsyncDB):
    while True:
        now = datetime.now()
        states = await db.get_all_states()

        for state in states:
            user_id = state[1]
            step = state[5]
            checkin_str = state[9]
            username = state[2]
            if step != "completed_checkin":
                continue
            if not checkin_str:
                continue
            try:
                checkin_time = datetime.strptime(checkin_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue
            time_diff = now - checkin_time
            try:
                # Напоминание через 15 часов
                if timedelta(minutes=3) < time_diff <= timedelta(minutes=5):
                    await bot.send_message(int(user_id), "🔔 Напоминание: не забудь завершить смену!")
                # Если прошло больше суток — сброс состояния, ожидание нового чек-ина
                elif time_diff > timedelta(minutes=5):
                    mark_incomplete_shift(username)
                    await bot.send_message(int(user_id), "😢 Ты не завершил смену в течение суток. Сохраняю как незавершённую. Теперь можешь начать новую смену, отправив фото для чек-ина.")
                    await db.delete_state(user_id)
            except Exception as e:
                logging.warning(f"Не удалось отправить сообщение {user_id}: {e}")
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)