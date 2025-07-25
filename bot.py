import asyncio
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import main
from utils.bot_instance import bot 
from utils.state_watcher import check_user_states
from utils.db import AsyncDB

async def main_entry():
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(main.router)
    db = AsyncDB("data/user_states.db")
    # Запуск напоминаний
    asyncio.create_task(check_user_states(bot, db))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main_entry())