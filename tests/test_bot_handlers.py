import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from src.bot import dp, start_commands, sing_up, set_username, set_email, set_age
from src.states.user_states import RegistrationState
from src.utils.messages import MESSAGES


class TestBotHandlers:
    @pytest.fixture
    async def mock_message(self):
        """Создает mock сообщение для тестов"""
        message = AsyncMock(spec=types.Message)
        message.text = "test_text"
        message.from_user.id = 12345
        message.from_user.username = "test_user"
        message.reply = AsyncMock()
        message.answer = AsyncMock()
        return message

    @pytest.fixture
    async def mock_state(self):
        """Создает mock состояние FSM"""
        state = AsyncMock(spec=FSMContext)
        state.get_data = AsyncMock(return_value={})
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()
        state.clear = AsyncMock()
        return state

    async def test_start_command(self, mock_message):
        """Тестирует команду /start"""
        await start_commands(mock_message)
        mock_message.answer.assert_called_once_with(
            MESSAGES["start"],
            reply_markup=ANY,  # Здесь будет клавиатура, которую нужно импортировать
            parse_mode="HTML"
        )

    async def test_sing_up_command(self, mock_message, mock_state):
        """Тестирует команду регистрации"""
        await sing_up(mock_message, mock_state)

        mock_message.answer.assert_called_once_with(
            MESSAGES["registration_start"],
            parse_mode="HTML"
        )
        mock_state.set_state.assert_called_once_with(RegistrationState.username)

    @patch('src.bot.is_valid_username')
    @patch('src.bot.is_included')
    @patch('src.bot.add_user')
    async def test_set_username_valid(self, mock_add_user, mock_is_included, mock_is_valid_username, mock_message,
                                      mock_state):
        """Тестирует установку валидного имени пользователя"""
        mock_is_valid_username.return_value = (True, "")
        mock_is_included.return_value = False

        mock_message.text = "valid_username"

        await set_username(mock_message, mock_state)

        mock_state.update_data.assert_called_once_with(username="valid_username")
        mock_state.set_state.assert_called_once_with(RegistrationState.email)

    @patch('src.bot.is_valid_username')
    async def test_set_username_invalid(self, mock_is_valid_username, mock_message, mock_state):
        """Тестирует установку невалидного имени пользователя"""
        mock_is_valid_username.return_value = (False, "Ошибка валидации")
        mock_message.text = "invalid_username"

        await set_username(mock_message, mock_state)

        mock_message.reply.assert_called_once_with("Ошибка валидации", parse_mode="HTML")
        mock_state.update_data.assert_not_called()

    @patch('src.bot.is_valid_email')
    @patch('src.bot.add_user')
    async def test_set_email_valid(self, mock_add_user, mock_is_valid_email, mock_message, mock_state):
        """Тестирует установку валидного email"""
        mock_is_valid_email.return_value = (True, "")
        mock_message.text = "test@example.com"

        await set_email(mock_message, mock_state)

        mock_state.update_data.assert_called_once_with(email="test@example.com")
        mock_state.set_state.assert_called_once_with(RegistrationState.age)

    async def test_set_age_valid(self, mock_message, mock_state):
        """Тестирует установку валидного возраста"""
        mock_message.text = "25"

        with patch('src.bot.add_user') as mock_add_user:
            await set_age(mock_message, mock_state)

            mock_add_user.assert_called_once()
            mock_state.clear.assert_called_once()

    async def test_set_age_invalid(self, mock_message, mock_state):
        """Тестирует установку невалидного возраста"""
        mock_message.text = "invalid_age"

        await set_age(mock_message, mock_state)

        mock_message.reply.assert_called_once_with(
            MESSAGES["invalid_number"],
            parse_mode="HTML"
        )

    async def test_set_age_out_of_range(self, mock_message, mock_state):
        """Тестирует установку возраста вне диапазона"""
        mock_message.text = "200"  # Слишком старый

        await set_age(mock_message, mock_state)

        mock_message.reply.assert_called_once_with(
            MESSAGES["age_fail"],
            parse_mode="HTML"
        )