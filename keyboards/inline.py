from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def direction_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Волонтеры-инструкторы", callback_data="Волонтеры-инструкторы")],
        [InlineKeyboardButton(text="Основные форматы", callback_data="Основные форматы")],
        [InlineKeyboardButton(text="Сервисное сопровождение", callback_data="Сервисное сопровождение")],
        [InlineKeyboardButton(text="Штаб/Медиа", callback_data="Штаб/Медиа")],
        [InlineKeyboardButton(text="Сопровождение событий", callback_data="Сопровождение событий")],
        [InlineKeyboardButton(text="Работа с участниками", callback_data="Работа с участниками")],
        [InlineKeyboardButton(text="Работа со зрителям и аккредитация", callback_data="Работа со зрителям и аккредитация")],
    ])
    return keyboard