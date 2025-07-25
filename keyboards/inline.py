from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def direction_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Инструкторы", callback_data="Инструкторы")],
        [InlineKeyboardButton(text="Образовалка", callback_data="Образовалка")],
        [InlineKeyboardButton(text="Ивент", callback_data="Ивент")],
    ])
    return keyboard