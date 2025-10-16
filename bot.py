# bot.py
import asyncio
import re
import matplotlib as mpl
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from better_profanity import profanity
from config import BOT_TOKEN
from crud_functions import *
from keyboards.inline_keyboards import activity_keyboard, formulasses, kb_line, profile_keyboard
from keyboards.reply_keyboards import kb, kb_registered
from states.user_states import RegistrationExercise, RegistrationState, UserState
from utils.bad_words import forbidden_words
from utils.messages import MESSAGES

mpl.use('Agg')
BOT_TOKEN_ERROR_MSG_BOT = "BOT_TOKEN не установлен. Проверьте файл .env"
if not BOT_TOKEN:
    raise ValueError(BOT_TOKEN_ERROR_MSG_BOT)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

user_last_data = {}


@dp.message(Command(commands=['start']))
async def start_commands(message: types.Message):
    # ИЗМЕНЕНО: Проверяем регистрацию и показываем соответствующее меню
    if user_exists(message.from_user.id):
        await message.answer(MESSAGES["start"], reply_markup=kb_registered, parse_mode="HTML")
    else:
        await message.answer(MESSAGES["start"], reply_markup=kb, parse_mode="HTML")


@dp.message(F.text == '👤 Регистрация')
async def sing_up(message: types.Message, state: FSMContext):
    if user_exists(message.from_user.id):
        await message.answer("❌ Вы уже зарегистрированы!")
        return

    await message.answer(MESSAGES["registration_start"], parse_mode="HTML")
    await state.set_state(RegistrationState.username)


@dp.message(StateFilter(RegistrationState.username))
async def set_username(message: types.Message, state: FSMContext):
    username = message.text

    is_valid, error_msg = is_valid_username(username)
    if not is_valid:
        await message.reply(error_msg, parse_mode="HTML")
        return

    bool_name = is_included(username)
    if bool_name:
        await message.reply(MESSAGES["user_exists"], parse_mode="HTML")
        return

    await state.update_data(username=username)
    await state.set_state(RegistrationState.email)
    await message.reply(MESSAGES["enter_email"], parse_mode="HTML")


@dp.message(StateFilter(RegistrationState.email))
async def set_email(message: types.Message, state: FSMContext):
    email = message.text
    is_valid, error_msg = is_valid_email(email)
    if not is_valid:
        await message.reply(error_msg, parse_mode="HTML")
        return
    await state.update_data(email=email)
    await state.set_state(RegistrationState.age)
    await message.reply(MESSAGES["enter_age"], parse_mode="HTML")


@dp.message(StateFilter(RegistrationState.age))
async def set_age(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        if age < 0 or age > 150:
            await message.reply(MESSAGES["age_fail"], parse_mode="HTML")
            return
    except ValueError:
        await message.reply(MESSAGES["invalid_number"], parse_mode="HTML")
        return

    data = await state.get_data()
    username = data.get('username')
    email = data.get('email')
    telegram_id = message.from_user.id
    add_user(username, email, age, telegram_id)
    await message.reply(MESSAGES["registration_success"], parse_mode="HTML")
    await message.answer(MESSAGES["start"], reply_markup=kb_registered, parse_mode="HTML")
    await state.clear()


@dp.message(F.text == '🧮 Калорийность')
async def main_menu(message: types.Message):
    await message.answer("Выберите опцию:", reply_markup=kb_line, parse_mode="HTML")


@dp.callback_query(F.data == 'calories')
async def calories_callback(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(MESSAGES["calorie_calc_start"], parse_mode="HTML")
    await call.answer()
    await state.set_state(UserState.age)


@dp.callback_query(F.data == 'formulas')
async def get_formulas(call: types.CallbackQuery):
    await call.message.answer(MESSAGES["formulas"], parse_mode="HTML")
    await call.answer()


@dp.message(StateFilter(UserState.age))
async def set_age_for_calories(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        if age < 0 or age > 150:
            await message.reply(MESSAGES["age_fail"], parse_mode="HTML")
            return
    except ValueError:
        await message.reply(MESSAGES["invalid_number"], parse_mode="HTML")
        return

    await state.update_data(age=age)

    # Сохраняем возраст в последних данных пользователя
    user_id = message.from_user.id
    if user_id not in user_last_data:
        user_last_data[user_id] = {}
    user_last_data[user_id]['age'] = age

    await message.answer(MESSAGES['enter_gender'], parse_mode="HTML")
    await state.set_state(UserState.sex)


@dp.message(StateFilter(UserState.sex))
async def set_sex(message: types.Message, state: FSMContext):
    try:
        sex_input = int(message.text)
        if sex_input not in [1, 2]:
            await message.reply(MESSAGES['enter_gender'], parse_mode="HTML")
            return
    except ValueError:
        await message.reply("Пожалуйста, введите 1 или 2:")
        return

    sex_value = 5 if sex_input == 1 else -161
    await state.update_data(sex=sex_value)

    # Сохраняем пол в последних данных
    user_id = message.from_user.id
    user_last_data[user_id]['sex'] = 'Мужской' if sex_value == 5 else 'Женский'

    await message.answer(MESSAGES['enter_height'], parse_mode="HTML")
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

    # Сохраняем рост в последних данных
    user_id = message.from_user.id
    user_last_data[user_id]['growth'] = growth

    await message.answer(MESSAGES['enter_weight'], parse_mode="HTML")
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

    # Сохраняем вес в последних данных
    user_id = message.from_user.id
    user_last_data[user_id]['weight'] = weight

    await message.answer(MESSAGES['choose_activity'], reply_markup=activity_keyboard, parse_mode="HTML")
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
    activity = data.get('activity')
    growth = data.get('growth')
    weight = data.get('weight')

    if all(param is not None for param in [age, sex, growth, weight, activity]):
        bmr = 10 * weight + 6.25 * growth - 5 * age + sex
        total_calories = bmr * activity
        Plus = total_calories * 1.20
        Minus = total_calories * 0.85

        await call.message.answer(f'''✅ <b>Расчет завершен!</b>

📊 <b>Ваши данные:</b>
• Возраст: {age} лет
• Пол: {'Мужской' if sex == 5 else 'Женский'}
• Рост: {growth} см
• Вес: {weight} кг
• Коэффициент активности: {activity}
🔥 <b>Ваша суточная норма калорий: {total_calories:.0f} ккал</b>''', parse_mode="HTML")
        await call.message.answer("Выберите опцию:", reply_markup=formulasses)

        await state.update_data(
            total_calories=total_calories,
            plus_calories=Plus,
            minus_calories=Minus
        )
    else:
        await call.message.answer('Произошла ошибка в данных. Попробуйте заново.')

    await state.set_state(None)


@dp.callback_query(F.data == 'minus')
async def handle_minus(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    minus_calories = data.get('minus_calories', 0)
    await call.message.answer(
        f"Вы выбрали похудение. Рекомендуем уменьшить калорийность на 15-20%. В вашем случае это {minus_calories:.0f}")
    await call.answer()


@dp.callback_query(F.data == 'plus')
async def handle_plus(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    plus_calories = data.get('plus_calories', 0)
    await call.message.answer(
        f"Вы выбрали набор массы. Рекомендуем увеличить калорийность на 10-20%. В вашем случае это {plus_calories:.0f}")
    await call.answer()


@dp.callback_query(F.data == 'nolik')
async def handle_nolik(call: types.CallbackQuery):
    await call.message.answer("Вы выбрали поддержание веса. Рекомендуем придерживаться рассчитанной нормы калорий.")
    await call.answer()


# ИЗМЕНЕНО: Обновленная функция записи подходов с привязкой к telegram_id
@dp.message(F.text == '💪 Подход')
async def exercise(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data(telegram_id=user_id)  # Сохраняем telegram_id пользователя
    await message.answer("Введите название упражнения")
    await state.set_state(RegistrationExercise.name_exercise)


@dp.message(StateFilter(RegistrationExercise.name_exercise))
async def set_exer(message: types.Message, state: FSMContext):
    name_exercise = message.text
    data = await state.get_data()
    user_id = data.get('telegram_id')  # Получаем telegram_id пользователя

    # ИЗМЕНЕНО: Теперь проверяем существование упражнения у конкретного пользователя
    if exercise_exists(name_exercise, user_id):
        await message.reply(
            'Такое упражнение уже существует у вас. Хотите обновить результаты? (да/нет)')
        await state.update_data(name_exercise=name_exercise)  # Сохраняем имя для дальнейшего использования
        await state.set_state(RegistrationExercise.confirm_update)
    else:
        await state.update_data(name_exercise=name_exercise)
        await state.set_state(RegistrationExercise.working_weight)
        await message.reply("Укажите ваш рабочий вес:")


# ИЗМЕНЕНО: Новый обработчик для подтверждения обновления
@dp.message(StateFilter(RegistrationExercise.confirm_update))
async def confirm_update(message: types.Message, state: FSMContext):
    response = message.text.lower()
    data = await state.get_data()
    name_exercise = data.get('name_exercise')
    user_id = data.get('telegram_id')

    if response in ['да', 'yes', 'обновить']:
        # Продолжаем с обновлением
        await message.reply("Укажите новый рабочий вес:")
        await state.set_state(RegistrationExercise.working_weight)
    elif response in ['нет', 'no', 'новое']:
        await message.reply("Введите другое название упражнения:")
        await state.set_state(RegistrationExercise.name_exercise)
    else:
        await message.reply("Пожалуйста, ответьте 'да' или 'нет':")


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
    user_id = data.get('telegram_id')  # Получаем telegram_id для привязки

    # ИЗМЕНЕНО: Проверяем существование упражнения у конкретного пользователя и решаем: добавить или обновить
    if exercise_exists(name_exercise, user_id):
        update_exercise(name_exercise, working_weight, iteration, user_id)
        await message.reply(
            f"✅ Результаты упражнения '{name_exercise}' обновлены!\n"
            f"🏋️ Вес: {working_weight} кг | 🔄 Повторений: {iteration}")
    else:
        add_exercise(name_exercise, working_weight, iteration, user_id)  # Передаем telegram_id
        await message.reply(
            f"✅ Новый подход записан!\n"
            f"💪 Упражнение: {name_exercise}\n"
            f"🏋️ Вес: {working_weight} кг | 🔄 Повторений: {iteration}")

    await state.clear()


@dp.message(F.text == '👤 Мой профиль')
async def show_profile(message: types.Message):
    user_data = get_user_data(message.from_user.id)

    if user_data:  # ИСПРАВЛЕНО: добавлено двоеточие
        profile_text = f"""👤 <b>Ваш профиль:</b>

🆔 ID: {message.from_user.id}
📝 Имя: {user_data['username']}
📧 Email: {user_data['email']}
🎂 Возраст: {user_data['age']} лет

/stats - Статистика тренировок"""

        await message.answer(profile_text, reply_markup=profile_keyboard, parse_mode="HTML")
    else:
        await message.answer("❌ Профиль не найден. Пройдите регистрацию.")


@dp.callback_query(F.data.startswith("edit_"))
async def edit_profile_callback(call: types.CallbackQuery, state: FSMContext):
    action = call.data.split("_")[1]

    if action == "username":
        await call.message.answer("Введите новое имя пользователя:")
        await state.set_state(RegistrationState.username)
    elif action == "email":
        await call.message.answer("Введите новый email:")
        await state.set_state(RegistrationState.email)
    elif action == "age":
        await call.message.answer("Введите новый возраст:")
        await state.set_state(RegistrationState.age)
    elif action == "main_menu":
        await call.message.answer("Возвращаемся в главное меню", reply_markup=kb)

    await call.answer()


@dp.message(StateFilter(RegistrationState.username))
async def update_username(message: types.Message, state: FSMContext):
    username = message.text
    is_valid, error_msg = is_valid_username(username)
    if not is_valid:
        await message.reply(error_msg, parse_mode="HTML")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Users SET username = ? WHERE telegram_id = ?",
                       (username, message.from_user.id))
        conn.commit()
        await message.reply(f"✅ Имя успешно изменено на: {username}")
    finally:
        conn.close()
    await state.clear()


@dp.message(StateFilter(RegistrationState.email))
async def update_email(message: types.Message, state: FSMContext):
    email = message.text
    is_valid, error_msg = is_valid_email(email)
    if not is_valid:
        await message.reply(error_msg, parse_mode="HTML")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Users SET email = ? WHERE telegram_id = ?",
                       (email, message.from_user.id))
        conn.commit()
        await message.reply(f"✅ Email успешно изменен на: {email}")
    finally:
        conn.close()
    await state.clear()


@dp.message(StateFilter(RegistrationState.age))
async def update_age(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        if age < 0 or age > 150:
            await message.reply(MESSAGES["age_fail"], parse_mode="HTML")
            return
    except ValueError:
        await message.reply(MESSAGES["invalid_number"], parse_mode="HTML")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Users SET age = ? WHERE telegram_id = ?",
                       (age, message.from_user.id))
        conn.commit()
        await message.reply(f"✅ Возраст успешно изменен на: {age}")
    finally:
        conn.close()
    await state.clear()


# ИЗМЕНЕНО: Новые обработчики для отслеживания прогресса
@dp.message(Command(commands=['progress']))
async def show_progress_options(message: types.Message):
    """Показать варианты просмотра прогресса"""
    exercises = get_all_user_exercises(message.from_user.id)

    if not exercises:
        await message.answer("❌ У вас пока нет записанных упражнений.")
        return

    # Создаем клавиатуру с упражнениями
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for exercise in exercises:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text=exercise, callback_data=f"progress_{exercise}")
        ])

    await message.answer("📊 <b>Выберите упражнение для просмотра прогресса:</b>",
                         reply_markup=keyboard, parse_mode="HTML")


@dp.callback_query(F.data.startswith("progress_"))
async def show_exercise_progress(call: types.CallbackQuery):
    """Показать прогресс по выбранному упражнению"""
    exercise_name = call.data.split("_", 1)[1]
    user_id = call.from_user.id

    # Генерируем график
    chart_buffer = generate_progress_chart(exercise_name, user_id)

    if chart_buffer:
        # Отправляем график
        chart_buffer.name = f"progress_{exercise_name}.png"
        photo = types.input_file.BufferedInputFile(chart_buffer.read(), filename=f"progress_{exercise_name}.png")
        await call.message.answer_photo(photo=photo, caption=f"📈 Прогресс по упражнению: <b>{exercise_name}</b>",
                                        parse_mode="HTML")

        # Также отправляем текстовую статистику
        progress_data = get_exercise_progress(exercise_name, user_id)
        if progress_data:
            first_weight = progress_data[0][0]
            last_weight = progress_data[-1][0]
            improvement = last_weight - first_weight

            stats_text = f"""📊 <b>Статистика прогресса по {exercise_name}:</b>

📈 Начальный вес: {first_weight} кг
🎯 Текущий вес: {last_weight} кг
✅ Прогресс: {improvement:+.1f} кг

"""
            if improvement > 0:
                stats_text += "🎉 Отличный прогресс! Вы прибавили в силе!"
            elif improvement == 0:
                stats_text += "💪 Вы держите стабильный вес, продолжайте в том же духе!"
            else:
                stats_text += "💪 Не расстраивайтесь! Прогресс требует времени."

            await call.message.answer(stats_text, parse_mode="HTML")
    else:
        await call.message.answer(f"❌ Недостаточно данных для построения графика по упражнению: {exercise_name}")

    await call.answer()


@dp.message(Command(commands=['all_progress']))
async def show_all_progress(message: types.Message):
    """Показать общий прогресс по всем упражнениям"""
    exercises = get_all_user_exercises(message.from_user.id)

    if not exercises:
        await message.answer("❌ У вас пока нет записанных упражнений.")
        return

    progress_text = "📊 <b>Общий прогресс по всем упражнениям:</b>\n\n"

    for exercise in exercises:
        progress_data = get_exercise_progress(exercise, message.from_user.id, limit=10)
        if progress_data:
            first_weight = progress_data[0][0]
            last_weight = progress_data[-1][0]
            improvement = last_weight - first_weight

            progress_text += f"<b>{exercise}:</b>\n"
            progress_text += f"   📈 От {first_weight} кг до {last_weight} кг\n"
            progress_text += f"   ✅ Прогресс: {improvement:+.1f} кг\n\n"

    await message.answer(progress_text, parse_mode="HTML")


def is_russian_profanity(text: str) -> bool:
    text_lower = text.lower()
    for word in forbidden_words:
        if word in text_lower:
            return True
    return False


def is_valid_username(username: str) -> tuple[bool, str]:
    # Проверка длины
    if len(username) < 2 or len(username) > 30:
        return False, "Имя должно быть от 2 до 30 символов."

    # Проверка первого символа (не цифра)
    if username[0].isdigit():
        return False, "Имя не может начинаться с цифры."

    # Проверка на допустимые символы
    if not re.match(r'^[a-zA-Zа-яА-ЯёЁ0-9_-]+$', username):
        return False, "Имя содержит недопустимые символы."

    # Проверка на мат через better-profanity (английский)
    if profanity.contains_profanity(username):
        return False, "Имя содержит запрещённые слова."

    # Проверка на русский мат через кастомный список
    if is_russian_profanity(username):
        return False, "Имя содержит запрещённые слова."

    return True, ""


def is_valid_email(email: str) -> tuple[bool, str]:
    """
    Проверяет корректность email:
    - Соответствие формату email
    - He содержит запрещенных слов
    """
    # Проверка формата email с помощью регулярного выражения
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Некорректный формат email. Пример: user@example.com"

    # Проверка на запрещенные слова в email
    email_lower = email.lower()
    for forbidden_word in forbidden_words:
        if forbidden_word in email_lower:
            return False, "Email содержит запрещённые слова."

    # Проверка на мат через better-profanity (английский)
    if profanity.contains_profanity(email):
        return False, "Email содержит запрещённые слова."

    return True, ""


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
