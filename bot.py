import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)


BOT_TOKEN = os.getenv("BOT_TOKEN") 

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я фитнес-бот. Со мной ты будешь видеть результат своих тренировок и может даже что-то ещё, я незнаю пока чему меня научат точно 🏋️")

# Обработчик команды /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = """
🏋️ <b>Фитнес-бот - Помощь</b>

Список команд, которые я скоро научусь понимать:
/start - начать работу
/help - показать помощь
/log - внести результаты тренировки
/stats - посмотреть статистику
/today - показать сегодняшнюю тренировку
/profile - управление профилем

Я помогу тебе отслеживать прогресс в тренировках! 💪
"""
    await message.answer(help_text, parse_mode="HTML")

# Обработчик всех текстовых сообщений
@dp.message()
async def echo_message(message: types.Message):
    await message.answer(f"Я получил ваше сообщение: \"{message.text}\"\nНо пока не умею на него правильно отвечать 😊")

# Основная функция запуска
async def main():
    print("Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")