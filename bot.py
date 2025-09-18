from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from crud_functions import *
import asyncio
import aiogram

api = "7903285534:AAELmygqVRKdDzzjqZ0Ap2Dvu7m68jZKODs"
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())
kb = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
button4 = KeyboardButton(text='Регистрация')
kb.add(button, button2)
kb.add(button4)
kb_line = InlineKeyboardMarkup()
button_line = InlineKeyboardButton(text = 'Рассчитать норму калорий', callback_data='calories')
button_line2 = InlineKeyboardButton(text = 'Формулы расчёта', callback_data='formulas')


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()


@dp.message_handler(text='Регистрация')
async def sing_up(message):
    await message.answer("Введите имя пользователя (только латинский алфавит):")
    await RegistrationState.username.set()

@dp.message_handler(state=RegistrationState.username)
async def set_username(message: types.Message, state: FSMContext):
    username = message.text
    bool_name = is_included(username)
    if bool_name is True:
        await message.reply("Пользователь существует, введите другое имя:")
    else:
        await state.update_data(username=username)
        await RegistrationState.email.set()
        await message.reply("Введите свой email:")


@dp.message_handler(state=RegistrationState.email)
async def set_email(message: types.Message, state: FSMContext):
    email = message.text
    await state.update_data(email=email)
    await RegistrationState.age.set()
    await message.reply("Введите свой возраст:")


@dp.message_handler(state=RegistrationState.age)
async def set_age(message: types.Message, state: FSMContext):
    age = message.text
    data = await state.get_data()
    username = data.get('username')
    email = data.get('email')
    add_user(username, email, age)
    await message.reply("Вы успешно зарегистрированы!")
    await state.finish()

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer("Выберите опцию:", reply_markup=kb_line)

@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer("10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5")
    await call.answer ()



@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await call.answer()
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    await message.answer('Введите свой рост в сантиметрах:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=int(message.text))
    await message.answer('Введите свой вес в кг:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=int(message.text))
    data = await state.get_data()
    age = data.get('age')
    growth = data.get('growth')
    weight = data.get('weight')
    bmr = 10 * weight + 6.25 * growth - 5 * age + 5
    await message.answer(f'Ваша норма калорий: {bmr} ккал в день.')
    await state.finish()

class RegistrationExercise (StatesGroup):
    name_exercise = State ()
    working_weight = State ()
    iteration = State ()

@dp.message_handler(text='Записать результат подхода')
async def exercise(message):
    await message.answer("Введите название упражнения")
    await RegistrationExercise.name_exercise.set()

@dp.message_handler(state=RegistrationExercise.name_exercise)
async def set_exer(message: types.Message, state: FSMContext):
    name_exercise = message.text
    bool_name = is_included(name_exercise)
    if bool_name is True:
        await message.reply('Такое упражнение уже существует, хотите обновить показатели? тогда используйте "Обновление данных".')
    else:
        await state.update_data(name_exercise=name_exercise)
        await RegistrationExercise.working_weight.set()
        await message.reply("Укажите ваш рабочий вес:")

@dp.message_handler(state=RegistrationExercise.working_weight)
async def set_working_weight(message: types.Message, state: FSMContext):
    working_weight = message.text
    await state.update_data(working_weight=working_weight)
    await RegistrationExercise.iteration.set()
    await message.reply("Укажите количество повторений")

@dp.message_handler(state=RegistrationExercise.iterarion)
async def set_iteration(message: types.Message, state: FSMContext):
    iteration = message.text
    data = await state.get_data()
    name_exercise = data.get('name_exercise')
    working_weight = data.get('working_weight')
    add_exercise(name_exercise, working_weight, iteration)
    await message.reply("Ну после такого подхода вас трудно не похвалить, так держать наша цель здоровье и красивое тело😉")
    await state.finish()

@dp.message_handler(commands=['start'])
async def start_commands(message):
    await message.answer("Привет! Я бот",
                         reply_markup=kb)

@dp.message_handler(text = 'Информация')
async def information(message):
    await message.answer('Кнопка еще не готова')

@dp.message_handler()
async def all_message(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
