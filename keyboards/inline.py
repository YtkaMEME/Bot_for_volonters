from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def direction_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Волонтёры-инструкторы", callback_data="Инструкторы")],
        [InlineKeyboardButton(text="Основные форматы", callback_data="Форматы")],
        [InlineKeyboardButton(text="Сервисное сопровождение", callback_data="Сервис")],
        [InlineKeyboardButton(text="Штаб / Медиа", callback_data="ШтабМедиа")],
        [InlineKeyboardButton(text="Сопровождение событий", callback_data="События")],
        [InlineKeyboardButton(text="Работа с участниками", callback_data="Участники")],
        [InlineKeyboardButton(text="Работа со зрителями и аккредитация", callback_data="Зрители")],
    ])
    return keyboard