from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.inline import direction_keyboard
from utils.sheets import write_checkin, write_checkout
from utils.drive import save_volunteer_photo
from utils.db import AsyncDB
from config import BOT_TOKEN, IMAGES_DIR, BASE_URL
from datetime import datetime
from aiogram.filters import Command
from aiogram.filters import CommandStart
import os
from utils.bot_instance import bot 

router = Router()

DB_PATH = "data/user_states.db"
os.makedirs("data", exist_ok=True)
db = AsyncDB(DB_PATH)

class CheckinStates(StatesGroup):
    waiting_photo = State()
    waiting_direction = State()
    checked_in = State()

@router.message((Command("start")))
async def cmd_start(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    # Сбросить состояние FSM и удалить состояние из базы
    await state.clear()
    await db.delete_state(user_id)
    text = (
        f"Привет, {message.from_user.full_name}! 👋\n\n"
        "Я — бот для учёта волонтёров.\n\n"
        "Чтобы начать смену, просто отправь мне свою фотографию (селфи).\n"
        "Я помогу тебе отметить чек-ин, выбрать направление и завершить смену.\n\n"
        "Если возникнут вопросы — просто напиши /start ещё раз!"
    )
    await message.answer(text)

@router.message()
async def handle_photo(message: Message, state: FSMContext):
    if message.media_group_id:
        await message.answer("⚠️ Пожалуйста, отправь только *одну* фотографию, а не альбом!", parse_mode="Markdown")
        return
    if message.content_type != "photo":
        await message.answer("⚠️ Пожалуйста, отправь только одно фото.")
        return

    user_id = str(message.from_user.id)
    username = message.from_user.username or f"id_{user_id}"
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M")
    full_name = message.from_user.full_name

    fsm_data = await state.get_data()
    user_state = await db.get_state(user_id)
    wait_msg = await message.answer("⏳ Обрабатываю фото... Это может занять несколько секунд ☁️📸")

    try:
        is_checkin = not user_state or user_state[5] != "completed_checkin"
        photo_drive_url = await save_volunteer_photo(
            bot,
            message.photo[-1].file_id,
            full_name,
            is_checkin
        )
        if not photo_drive_url:
            await message.answer("❌ Не удалось загрузить фото на сервере")
            return
    except Exception as e:
        await message.answer(f"❌ Ошибка загрузки фото: {e}")
        return
    finally:
        try:
            await wait_msg.delete()
        except Exception:
            pass

    if not user_state or user_state[7] != today:
        await message.answer("Привет! Укажи своё направление:", reply_markup=direction_keyboard())
        await db.save_state(user_id, {
            "username": username,
            "name": full_name,
            "direction": None,
            "step": "awaiting_direction",
            "photo_checkin": photo_drive_url,
            "date": today,
            "time_checkin": current_time,
            "checkin_datetime": now.strftime("%Y-%m-%d %H:%M:%S")
        })
        await state.set_state(CheckinStates.waiting_direction)
        await state.update_data(photo_checkin=photo_drive_url, username=username, name=full_name, date=today, time_checkin=current_time, checkin_datetime=now.strftime("%Y-%m-%d %H:%M:%S"))
    elif user_state[5] == "completed_checkin":
        write_checkout(username, current_time, photo_drive_url)
        await message.answer("Спасибо, ты успешно отметил завершение смены 💫 \n\nТеперь, чтобы начать новую смену, просто отправь селфи (для этого не нужно запускать бот ещё раз)")
        await db.delete_state(user_id)
        await state.clear()
    else:
        await message.answer("Сначала выбери своё направление ниже 👇")

@router.callback_query(F.data.in_(["Инструкторы", "Образовалка", "Ивент"]))
async def handle_direction(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    user_state = await db.get_state(user_id)
    if not user_state or user_state[5] != "awaiting_direction":
        return

    direction = callback.data
    updated_data = {
        "username": user_state[2],
        "name": callback.from_user.full_name,
        "direction": direction,
        "step": "completed_checkin",
        "photo_checkin": user_state[6],
        "date": user_state[7],
        "time_checkin": user_state[8],
        "checkin_datetime": user_state[9]
    }
    await db.save_state(user_id, updated_data)
    await state.set_state(CheckinStates.checked_in)
    await state.update_data(direction=direction)

    write_checkin(
        user_id=user_id,
        username=user_state[2],
        name=callback.from_user.full_name,
        direction=direction,
        time=user_state[8],
        photo_file_id=user_state[6]
    )
    await callback.message.edit_text(
        "Ты успешно отметил начало смены ✅\n\n"
        "Чтобы завершить смену, просто отправь селфи с завершением (для этого не нужно запускать бот заново)"
    )