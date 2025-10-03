import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import io
import base64


def get_db_connection():
    return sqlite3.connect('fitness.db')


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Exercise(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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


def ensure_date_column():
    """Убедиться, что колонка date существует в таблице Exercise"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Получить список колонок в таблице Exercise
    cursor.execute("PRAGMA table_info(Exercise)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'date' not in columns:
        try:
            cursor.execute("ALTER TABLE Exercise ADD COLUMN date TEXT")
            conn.commit()
            print("Колонка 'date' добавлена в таблицу 'Exercise'")
        except sqlite3.OperationalError as e:
            print(f"Ошибка при добавлении колонки 'date': {e}")

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


def exercise_exists(name_exercise, telegram_id):
    """Проверить, существует ли упражнение у конкретного пользователя"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM Exercise WHERE name_exercise = ? AND user_id = ?", (name_exercise, telegram_id))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def add_exercise(name_exercise, working_weight, iteration, telegram_id):
    """Добавить упражнение с привязкой к пользователю по telegram_id"""
    ensure_date_column()  # Убедиться, что колонка date существует
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Exercise (name_exercise, working_weight, iteration, user_id, date) VALUES (?, ?, ?, ?, datetime('now'))",
        (name_exercise, working_weight, iteration, telegram_id))
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


def update_exercise(name_exercise, working_weight, iteration, telegram_id):
    """Обновить результаты упражнения для конкретного пользователя"""
    ensure_date_column()  # Убедиться, что колонка date существует
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Exercise SET working_weight = ?, iteration = ?, date = datetime('now') WHERE name_exercise = ? AND user_id = ?",
        (working_weight, iteration, name_exercise, telegram_id))
    conn.commit()
    conn.close()


def get_user_exercises(telegram_id):
    """Получить все упражнения пользователя по telegram_id"""
    ensure_date_column()  # Убедиться, что колонка date существует
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name_exercise, working_weight, iteration, date FROM Exercise WHERE user_id = ?",
                   (telegram_id,))
    exercises = cursor.fetchall()
    conn.close()
    return exercises


def get_exercise_progress(name_exercise, telegram_id, limit=20):
    """Получить историю прогресса по конкретному упражнению"""
    ensure_date_column()  # Убедиться, что колонка date существует
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT working_weight, iteration, date 
        FROM Exercise 
        WHERE name_exercise = ? AND user_id = ? 
        ORDER BY date ASC 
        LIMIT ?
    """, (name_exercise, telegram_id, limit))
    progress = cursor.fetchall()
    conn.close()
    return progress


def generate_progress_chart(name_exercise, telegram_id):
    """Сгенерировать график прогресса по упражнению"""
    progress_data = get_exercise_progress(name_exercise, telegram_id)

    if not progress_data:  # ИСПРАВЛЕНО: используем правильное имя переменной
        return None

    dates = []
    weights = []

    for weight, reps, date_str in progress_data:  # ИСПРАВЛЕНО: используем правильное имя переменной
        dates.append(datetime.strptime(date_str[:19], '%Y-%m-%d %H:%M:%S'))
        weights.append(weight)

    plt.figure(figsize=(10, 6))
    plt.plot(dates, weights, marker='o', linestyle='-', linewidth=2, markersize=6)
    plt.title(f'Прогресс по упражнению: {name_exercise}', fontsize=14, fontweight='bold')
    plt.xlabel('Дата', fontsize=12)
    plt.ylabel('Рабочий вес (кг)', fontsize=12)
    plt.grid(True, alpha=0.3)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.xticks(rotation=45)

    if len(dates) > 1:
        from numpy import polyfit, poly1d
        x_numeric = [i for i in range(len(dates))]
        z = polyfit(x_numeric, weights, 1)
        p = poly1d(z)
        plt.plot(dates, p(x_numeric), "--", alpha=0.8, color='red', label=f'Тренд: {z[0]:.2f} кг/день')
        plt.legend()

    plt.tight_layout()

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()

    return img_buffer

def get_all_user_exercises(telegram_id):
    """Получить список всех упражнений пользователя"""
    ensure_date_column()  # Убедиться, что колонка date существует
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT name_exercise FROM Exercise WHERE user_id = ?", (telegram_id,))
    exercises = cursor.fetchall()
    conn.close()
    return [ex[0] for ex in exercises]


# Инициализация БД при запуске
init_db()
