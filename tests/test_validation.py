import pytest
from src.bot import is_valid_username, is_valid_email


class TestValidation:
    def test_valid_username(self):
        """Тестирует валидные имена пользователей"""
        valid_usernames = [
            "test_user",
            "user123",
            "TestUser",
            "user_name_123",
            "a" * 30  # Максимальная длина
        ]

        for username in valid_usernames:
            is_valid, error_msg = is_valid_username(username)
            assert is_valid is True, f"Username '{username}' should be valid, but got error: {error_msg}"

    def test_invalid_username(self):
        """Тестирует невалидные имена пользователей"""
        invalid_cases = [
            ("", "Имя должно быть от 2 до 30 символов."),
            ("a", "Имя должно быть от 2 до 30 символов."),
            ("a" * 31, "Имя должно быть от 2 до 30 символов."),
            ("123user", "Имя не может начинаться с цифры."),
            ("user@name", "Имя содержит недопустимые символы."),
            ("user name", "Имя содержит недопустимые символы."),
            ("user_name!", "Имя содержит недопустимые символы."),
        ]

        for username, expected_error in invalid_cases:
            is_valid, error_msg = is_valid_username(username)
            assert is_valid is False, f"Username '{username}' should be invalid"
            assert error_msg == expected_error, f"Expected '{expected_error}', got '{error_msg}'"

    def test_valid_email(self):
        """Тестирует валидные email"""
        valid_emails = [
            "test@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk",
            "user123@test-domain.org"
        ]

        for email in valid_emails:
            is_valid, error_msg = is_valid_email(email)
            assert is_valid is True, f"Email '{email}' should be valid, but got error: {error_msg}"

    def test_invalid_email(self):
        """Тестирует невалидные email"""
        invalid_cases = [
            ("", "Некорректный формат email. Пример: user@example.com"),
            ("invalid-email", "Некорректный формат email. Пример: user@example.com"),
            ("@example.com", "Некорректный формат email. Пример: user@example.com"),
            ("test@", "Некорректный формат email. Пример: user@example.com"),
            ("test@example", "Некорректный формат email. Пример: user@example.com"),
            ("test..example.com", "Некорректный формат email. Пример: user@example.com"),
        ]

        for email, expected_error in invalid_cases:
            is_valid, error_msg = is_valid_email(email)
            assert is_valid is False, f"Email '{email}' should be invalid"
            assert error_msg == expected_error, f"Expected '{expected_error}', got '{error_msg}'"