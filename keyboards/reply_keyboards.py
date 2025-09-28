from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='🧮 Калорийность'), KeyboardButton(text='ℹ️ Информация')],
        [KeyboardButton(text='👤 Регистрация'), KeyboardButton(text='💪 Подход')],
        [KeyboardButton(text='⚙️ Редактировать профиль')]
    ],
    resize_keyboard=True
)

kb_registered = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='🧮 Калорийность'), KeyboardButton(text='ℹ️ Информация')],
        [KeyboardButton(text='💪 Подход'), KeyboardButton(text='👤 Мой профиль')],
        [KeyboardButton(text='⚙️ Редактировать профиль')]
    ],
    resize_keyboard=True
)

kb_back = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='🏠 В меню')]
    ],
    resize_keyboard=True
)
