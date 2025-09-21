from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram import F
from crud_functions import *
import asyncio


api = "7903285534:AAELmygqVRKdDzzjqZ0Ap2Dvu7m68jZKODs"
bot = Bot(token=api)
dp = Dispatcher(storage=MemoryStorage())

kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Рассчитать суточную калорийность'), KeyboardButton(text='Информация')],
        [KeyboardButton(text='Регистрация'), KeyboardButton(text='Записать результат подхода')]
    ],
    resize_keyboard=True
)


kb_line = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')],
        [InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')]
    ]
)

formulasses = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Я хочу похудеть', callback_data='minus')],
        [InlineKeyboardButton(text='Я хочу набрать', callback_data='plus')],
        [InlineKeyboardButton(text='Хочу остаться в своем весе', callback_data='nolik')]
    ]
)

class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()
    sex = State()

class RegistrationExercise(StatesGroup):
    name_exercise = State()
    working_weight = State()
    iteration = State()

@dp.message(Command(commands=['start']))
async def start_commands(message: types.Message):
    await message.answer("Привет! Я бот для занятия спортом. Мои функции:", reply_markup=kb)

@dp.message(F.text == 'Регистрация')
async def sing_up(message: types.Message, state: FSMContext):
    await message.answer("Введите имя пользователя (только латинский алфавит):")
    await state.set_state(RegistrationState.username)

@dp.message(StateFilter(RegistrationState.username))
async def set_username(message: types.Message, state: FSMContext):
    username = message.text
    bool_name = is_included(username)
    if bool_name is True:
        await message.reply("Пользователь существует, введите другое имя:")
    else:
        await state.update_data(username=username)
        await state.set_state(RegistrationState.email)
        await message.reply("Введите свой email:")

@dp.message(StateFilter(RegistrationState.email))
async def set_email(message: types.Message, state: FSMContext):
    email = message.text
    await state.update_data(email=email)
    await state.set_state(RegistrationState.age)
    await message.reply("Введите свой возраст:")

@dp.message(StateFilter(RegistrationState.age))
async def set_age(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        if age < 0 or age > 150:
            await message.reply("Пожалуйста, введите корректный возраст (0-150):")
            return
    except ValueError:
        await message.reply("Пожалуйста, введите число:")
        return

    data = await state.get_data()
    username = data.get('username')
    email = data.get('email')
    add_user(username, email, age)
    await message.reply("Вы успешно зарегистрированы!")
    await state.clear()

@dp.message(F.text == 'Рассчитать суточную калорийность')
async def main_menu(message: types.Message):
    await message.answer("Выберите опцию:", reply_markup=kb_line)

@dp.callback_query(F.data == 'formulas')
async def get_formulas(call: types.CallbackQuery):
    await call.message.answer("10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5")
    await call.answer()


@dp.callback_query(F.data == 'calories')
async def calories_callback(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer('Введите свой возраст:')
    await call.answer()
    await state.set_state(UserState.age)


@dp.message(StateFilter(UserState.age))
async def set_age_for_calories(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        if age < 0 or age > 150:
            await message.reply("Пожалуйста, введите корректный возраст (0-150):")
            return
    except ValueError:
        await message.reply("Пожалуйста, введите число:")
        return

    await state.update_data(age=age)
    await message.answer('Укажите свой пол: мужчина - 1, женщина - 2')
    await state.set_state(UserState.sex)


@dp.message(StateFilter(UserState.sex))
async def set_sex(message: types.Message, state: FSMContext):
    try:
        sex_input = int(message.text)
        if sex_input not in [1, 2]:
            await message.reply("Пожалуйста, укажите свой пол: мужчина - 1, женщина - 2")
            return
    except ValueError:
        await message.reply("Пожалуйста, введите 1 или 2:")
        return

    sex_value = 5 if sex_input == 1 else -161
    await state.update_data(sex=sex_value)
    await message.answer('Введите свой рост в сантиметрах:')
    await state.set_state(UserState.growth)


@dp.message(StateFilter(UserState.growth))
async def set_growth(message: types.Message, state: FSMContext):
    try:
        growth = int(message.text)
        if growth < 50 or growth > 250:
            await message.reply("Пожалуйста, введите корректный рост (50-250 см):")
            return
    except ValueError:
        await message.reply("Пожалуйста, введите число:")
        return

    await state.update_data(growth=growth)
    await message.answer('Введите свой вес в кг:')
    await state.set_state(UserState.weight)


@dp.message(StateFilter(UserState.weight))
async def set_weight(message: types.Message, state: FSMContext):
    try:
        weight = float(message.text)
        if weight < 20 or weight > 300:
            await message.reply("Пожалуйста, введите корректный вес (20-300 кг):")
            return
    except ValueError:
        await message.reply("Пожалуйста, введите число:")
        return

    await state.update_data(weight=weight)
    data = await state.get_data()
    age = data.get('age')
    sex = data.get('sex')
    growth = data.get('growth')
    weight = data.get('weight')

    if all(param is not None for param in [age, sex, growth, weight]):
        bmr = 10 * weight + 6.25 * growth - 5 * age + sex
        Plus = bmr * 1.20
        Minus = bmr * 0.85
        await message.answer(f'Ваша норма калорий: {bmr:.0f} ккал в день.')
        await message.answer("Выберите опцию:", reply_markup=formulasses)
    else:
        await message.answer('Произошла ошибка в данных. Попробуйте заново.')

    await state.clear()

    @dp.callback_query(F.data == 'minus')
    async def handle_minus(call: types.CallbackQuery):
        await call.message.answer(f"Вы выбрали похудение. Рекомендуем уменьшить калорийность на 15-20%. В твоем случае это {Minus:0f}")
        await call.answer()

    @dp.callback_query(F.data == 'plus')
    async def handle_plus(call: types.CallbackQuery):
        await call.message.answer(f"Вы выбрали набор массы. Рекомендуем увеличить калорийность на 10-20%. В твоем случае это {Plus:0f}")
        await call.answer()

    @dp.callback_query(F.data == 'nolik')
    async def handle_nolik(call: types.CallbackQuery):
        await call.message.answer(
            "Вы выбрали поддержание веса. Рекомендуем придерживаться рассчитанной нормы калорий.")
        await call.answer()


    await state.clear()

@dp.message(F.text == 'Записать результат подхода')
async def exercise(message: types.Message, state: FSMContext):
    await message.answer("Введите название упражнения")
    await state.set_state(RegistrationExercise.name_exercise)

@dp.message(StateFilter(RegistrationExercise.name_exercise))
async def set_exer(message: types.Message, state: FSMContext):
    name_exercise = message.text
    bool_name = is_included(name_exercise)
    if bool_name is True:
        await message.reply('Такое упражнение уже существует, хотите обновить показатели? тогда используйте "Обновление данных".')
    else:
        await state.update_data(name_exercise=name_exercise)
        await state.set_state(RegistrationExercise.working_weight)
        await message.reply("Укажите ваш рабочий вес:")

@dp.message(StateFilter(RegistrationExercise.working_weight))
async def set_working_weight(message: types.Message, state: FSMContext):
    try:
        working_weight = float(message.text)
        if working_weight < 0 or working_weight > 1000:
            await message.reply("Пожалуйста, введите корректный вес (0-1000 кг):")
            return
    except ValueError:
        await message.reply("Пожалуйста, введите число:")
        return

    await state.update_data(working_weight=working_weight)
    await state.set_state(RegistrationExercise.iteration)
    await message.reply("Укажите количество повторений")

@dp.message(StateFilter(RegistrationExercise.iteration))
async def set_iteration(message: types.Message, state: FSMContext):
    try:
        iteration = int(message.text)
        if iteration < 0 or iteration > 1000:
            await message.reply("Пожалуйста, введите корректное количество повторений (0-1000):")
            return
    except ValueError:
        await message.reply("Пожалуйста, введите число:")
        return

    data = await state.get_data()
    name_exercise = data.get('name_exercise')
    working_weight = data.get('working_weight')
    add_exercise(name_exercise, working_weight, iteration)

    await message.reply("Ну после такого подхода вас трудно не похвалить, так держать наша цель здоровье и красивое тело😉")
    await state.clear()

@dp.message(F.text == 'Информация')
async def information(message: types.Message):
    await message.answer('Кнопка еще не готова')



@dp.message()
async def all_message(message: types.Message):
    await message.answer('Введите команду /start, чтобы начать общение.')

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
