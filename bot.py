from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram import F
from keyboards.reply_keyboards import kb
from keyboards.inline_keyboards import kb_line, formulasses, activity_keyboard
from states.user_states import RegistrationState, UserState, RegistrationExercise
from crud_functions import *
import asyncio
from config import BOT_TOKEN
from utils.messages import MESSAGES


if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен. Проверьте файл .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


@dp.message(Command(commands=['start']))
async def start_commands(message: types.Message):
    await message.answer(MESSAGES["start"], reply_markup=kb, parse_mode="HTML")

@dp.message(F.text == '👤 Регистрация')
async def sing_up(message: types.Message, state: FSMContext):
    await message.answer(MESSAGES["registration_start"], reply_markup=kb_back)
    await state.set_state(RegistrationState.username)

@dp.callback_query(F.data == 'calories')
async def calories_callback(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(MESSAGES["calorie_calc_start"], reply_markup=kb_back)
    await call.answer()
    await state.set_state(UserState.age)

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
    await message.answer('Выберите ваш уровень физической активности:', reply_markup=activity_keyboard)
    await state.set_state(UserState.activity)

@dp.callback_query(StateFilter(UserState.activity))
async def set_activity(call: types.CallbackQuery, state: FSMContext):
    activity_coefficient = float(call.data)
    await state.update_data(activity=activity_coefficient)
    await call.answer()

    # Получаем все данные и производим расчет
    data = await state.get_data()
    age = data.get('age')
    sex = data.get('sex')
    activity = data.get('activity')  # Исправлено: правильно получаем значение
    growth = data.get('growth')
    weight = data.get('weight')

    if all(param is not None for param in [age, sex, growth, weight, activity]):
        bmr = 10 * weight + 6.25 * growth - 5 * age + sex
        total_calories = bmr * activity
        Plus = total_calories * 1.20
        Minus = total_calories * 0.85
        await call.message.answer(f'Ваша норма калорий: {total_calories:.0f} ккал в день.')
        await call.message.answer("Выберите опцию:", reply_markup=formulasses)

        # Сохраняем значения для последующего использования
        await state.update_data(
            total_calories=total_calories,
            plus_calories=Plus,
            minus_calories=Minus
        )
    else:
        await call.message.answer('Произошла ошибка в данных. Попробуйте заново.')

    await state.set_state(None)  # Очищаем состояние


# Исправляем обработчики callback-запросов для формул
@dp.callback_query(F.data == 'minus')
async def handle_minus(call: types.CallbackQuery, state: FSMContext):  # Добавлен state как параметр
    data = await state.get_data()
    minus_calories = data.get('minus_calories', 0)
    await call.message.answer(
        f"Вы выбрали похудение. Рекомендуем уменьшить калорийность на 15-20%. В вашем случае это {minus_calories:.0f}")
    await call.answer()


@dp.callback_query(F.data == 'plus')
async def handle_plus(call: types.CallbackQuery, state: FSMContext):  # Добавлен state как параметр
    data = await state.get_data()
    plus_calories = data.get('plus_calories', 0)
    await call.message.answer(
        f"Вы выбрали набор массы. Рекомендуем увеличить калорийность на 10-20%. В вашем случае это {plus_calories:.0f}")
    await call.answer()


@dp.callback_query(F.data == 'nolik')
async def handle_nolik(call: types.CallbackQuery):
    await call.message.answer("Вы выбрали поддержание веса. Рекомендуем придерживаться рассчитанной нормы калорий.")
    await call.answer()


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