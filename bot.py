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

api = ""
bot = Bot(token=api)
dp = Dispatcher(storage=MemoryStorage())

# Исправленное создание клавиатур
kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Рассчитать'), KeyboardButton(text='Информация')],
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

class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

class RegistrationExercise(StatesGroup):
    name_exercise = State()
    working_weight = State()
    iteration = State()

# Исправленные хендлеры с синтаксисом aiogram 3.x
@dp.message(Command(commands=['start']))
async def start_commands(message: types.Message):
    await message.answer("Привет! Я бот", reply_markup=kb)

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
    age = message.text
    data = await state.get_data()
    username = data.get('username')
    email = data.get('email')
    add_user(username, email, age)
    await message.reply("Вы успешно зарегистрированы!")
    await state.clear()

@dp.message(F.text == 'Рассчитать')
async def main_menu(message: types.Message):
    await message.answer("Выберите опцию:", reply_markup=kb_line)

@dp.callback_query(F.text == 'formulas')
async def get_formulas(call: types.CallbackQuery):
    await call.message.answer("10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5")
    await call.answer()

@dp.callback_query(F.text == 'calories')
async def set_age(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer('Введите свой возраст:')
    await call.answer()
    await state.set_state(UserState.age)

@dp.message(StateFilter(UserState.age))
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    await message.answer('Введите свой рост в сантиметрах:')
    await state.set_state(UserState.growth)

@dp.message(StateFilter(UserState.growth))
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=int(message.text))
    await message.answer('Введите свой вес в кг:')
    await state.set_state(UserState.weight)

@dp.message(StateFilter(UserState.weight))
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=int(message.text))
    data = await state.get_data()
    age = data.get('age')
    growth = data.get('growth')
    weight = data.get('weight')
    bmr = 10 * weight + 6.25 * growth - 5 * age + 5
    await message.answer(f'Ваша норма калорий: {bmr} ккал в день.')
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
    working_weight = message.text
    await state.update_data(working_weight=working_weight)
    await state.set_state(RegistrationExercise.iteration)
    await message.reply("Укажите количество повторений")

@dp.message(StateFilter(RegistrationExercise.iteration))
async def set_iteration(message: types.Message, state: FSMContext):
    iteration = message.text
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
