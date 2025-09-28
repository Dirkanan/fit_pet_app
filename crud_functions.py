import sqlite3


def get_db_connection():
    return sqlite3.connect('fitness.db')


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Exercise(
        id INTEGER PRIMARY KEY,
        name_exercise TEXT NOT NULL,
        working_weight REAL NOT NULL,
        iteration INTEGER NOT NULL,
        user_id INTEGER
    )
    ''')


    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL,
        age INTEGER NOT NULL,
        telegram_id INTEGER UNIQUE
    )
    ''')

    # Таблица истории калорий
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS calorie_history (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        age INTEGER,
        gender TEXT,
        height REAL,
        weight REAL,
        activity REAL,
        calories REAL,
        date TEXT
    )
    ''')

    conn.commit()
    conn.close()


def add_user(username, email, age, telegram_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Users (username, email, age, telegram_id) VALUES (?, ?, ?, ?)",
                       (username, email, age, telegram_id))
        conn.commit()
    except sqlite3.IntegrityError:
        return False  # Пользователь уже существует
    finally:
        conn.close()
    return True


def is_included(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM Users WHERE username = ?", (username,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def exercise_exists(name_exercise):
    """Проверить, существует ли упражнение"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM Exercise WHERE name_exercise = ?", (name_exercise,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def add_exercise(name_exercise, working_weight, iteration, user_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Exercise (name_exercise, working_weight, iteration, user_id) VALUES (?, ?, ?, ?)",
                   (name_exercise, working_weight, iteration, user_id))
    conn.commit()
    conn.close()

def user_exists(telegram_id):
    """Проверить, зарегистрирован ли пользователь"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM Users WHERE telegram_id = ?", (telegram_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def get_user_data(telegram_id):
    """Получить данные пользователя по Telegram ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, email, age FROM Users WHERE telegram_id = ?", (telegram_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return {
            'username': user[0],
            'email': user[1],
            'age': user[2]
        }
    return None


# Инициализация БД при запуске
init_db()
