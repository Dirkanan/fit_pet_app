import sqlite3

connection = sqlite3.connect("Exercise.db")
cursor = connection.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS Exercise(
id INTEGER PRIMARY KEY,
name_exercise TEXT NOT NULL,
working_weight INTEGER NOT NULL ,
iteration INTEGER NOT NULL
)
''')

conn = sqlite3.connect('Users.db')
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS Users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT NOT NULL,
email TEXT NOT NULL,
age INTEGER NOT NULL
)
''')

conn.commit()


def add_user(username, email, age):
    check_user = cur.execute("SELECT * FROM Users WHERE username=?", (username,))
    if check_user.fetchone() is None:
        insert_query = """
        INSERT INTO Users (username, email, age) 
        VALUES (?, ?, ?);
        """
        cur.execute(insert_query, (username, email, age))
        conn.commit()


def is_included(username):
    select_query = "SELECT EXISTS(SELECT 1 FROM Users WHERE username=? LIMIT 1);"
    cur.execute(select_query, (username,))
    result = cur.fetchone()[0]
    return bool(result)


def add_exercise(name_exercise, working_weight, iteration):
    check_exercise = cur.execute("SELECT * FROM Exercise WHERE username=?", (name_exercise,))
    if check_exercise.fetchone() is None:
        insert_query = """
            INSERT INTO Exercise (name_exercise, working_weight, iteration) 
            VALUES (?, ?, ?);
            """
        cur.execute(insert_query, (name_exercise, working_weight, iteration))
        conn.commit()


connection.commit()


def get_all_exercise():
    connection = sqlite3.connect("Exercise.db")
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Exercise')
    exercise = cursor.fetchall()
    connection.close()
    return exercise


get_all_exercise()
conn.commit()

connection.commit()

