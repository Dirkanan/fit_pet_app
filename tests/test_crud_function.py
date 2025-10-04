import pytest
import sqlite3
import os
from unittest.mock import patch
from src.crud_functions import (
    init_db, add_user, is_included, exercise_exists, add_exercise,
    get_user_data, get_user_exercises, update_exercise
)


# Тесты для CRUD функций
class TestCRUDFunctions:
    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Создает временную базу данных для тестов"""
        self.db_path = "test_fitness.db"
        with patch('src.crud_functions.DATABASE_PATH', self.db_path):
            init_db()
        yield
        # Удаляем тестовую базу данных после тестов
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_add_user_and_is_included(self):
        """Тестирует добавление пользователя и проверку существования"""
        # Добавляем пользователя
        success = add_user("test_user", "test@example.com", 25)
        assert success is True

        # Проверяем, что пользователь существует
        assert is_included("test_user") is True
        assert is_included("nonexistent_user") is False

        # Проверяем добавление дубликата
        success = add_user("test_user", "another@example.com", 30)
        assert success is False

    def test_get_user_data(self):
        """Тестирует получение данных пользователя"""
        # Добавляем пользователя
        add_user("test_user", "test@example.com", 25)

        # Получаем данные
        user_data = get_user_data(1)  # Предполагаем, что ID будет 1
        assert user_data is not None
        assert user_data['username'] == "test_user"
        assert user_data['email'] == "test@example.com"
        assert user_data['age'] == 25

        # Проверяем, что возвращается None для несуществующего пользователя
        assert get_user_data(999) is None

    def test_add_and_get_exercise(self):
        """Тестирует добавление и получение упражнений"""
        # Добавляем пользователя
        add_user("test_user", "test@example.com", 25)

        # Добавляем упражнение
        add_exercise("Жим лежа", 80.0, 10, 1)  # user_id = 1

        # Проверяем, что упражнение существует
        assert exercise_exists("Жим лежа", 1) is True
        assert exercise_exists("Жим лежа", 2) is False  # Другой пользователь
        assert exercise_exists("Приседания", 1) is False  # Другое упражнение

        # Получаем упражнения пользователя
        exercises = get_user_exercises(1)
        assert len(exercises) == 1
        assert exercises[0][0] == "Жим лежа"
        assert exercises[0][1] == 80.0
        assert exercises[0][2] == 10

    def test_update_exercise(self):
        """Тестирует обновление упражнения"""
        # Добавляем пользователя и упражнение
        add_user("test_user", "test@example.com", 25)
        add_exercise("Жим лежа", 80.0, 10, 1)

        # Обновляем упражнение
        update_exercise("Жим лежа", 85.0, 12, 1)

        # Проверяем, что данные обновились
        exercises = get_user_exercises(1)
        assert len(exercises) == 1
        assert exercises[0][1] == 85.0  # Новый вес
        assert exercises[0][2] == 12  # Новое количество повторений