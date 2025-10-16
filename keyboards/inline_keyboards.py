from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

kb_line = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='🔥 Рассчитать калории', callback_data='calories')],
        [InlineKeyboardButton(text='🧮 Формулы расчета', callback_data='formulas')]
    ]
)

formulasses = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='📉 Похудеть', callback_data='minus')],
        [InlineKeyboardButton(text='📈 Набрать массу', callback_data='plus')],
        [InlineKeyboardButton(text='⚖️ Поддерживать вес', callback_data='nolik')]
    ]
)

activity_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='🛋️ Сидячий (1.2)', callback_data='1.2')],
        [InlineKeyboardButton(text='🚶 Легкая (1.375)', callback_data='1.375')],
        [InlineKeyboardButton(text='🚴 Умеренная (1.55)', callback_data='1.55')],
        [InlineKeyboardButton(text='🏃 Активная (1.725)', callback_data='1.725')],
        [InlineKeyboardButton(text='🏋️ Очень активная (1.9)', callback_data='1.9')]
    ]
)

profile_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Редактировать имя", callback_data="edit_username")],
        [InlineKeyboardButton(text="📧 Редактировать email", callback_data="edit_email")],
        [InlineKeyboardButton(text="🎂 Редактировать возраст", callback_data="edit_age")],
        [InlineKeyboardButton(text="🏠 B главное меню", callback_data="main_menu")]
    ]
)
