import pytest
from unittest.mock import patch
from src.bot import set_age_for_calories, set_sex, set_growth, set_weight, set_activity
from aiogram.fsm.context import FSMContext


class TestCalorieCalculation:
    @pytest.fixture
    async def mock_message(self):
        message = AsyncMock(spec=types.Message)
        message.text = "25"
        message.from_user.id = 12345
        message.reply = AsyncMock()
        message.answer = AsyncMock()
        return message

    @pytest.fixture
    async def mock_call(self):
        call = AsyncMock(spec=types.CallbackQuery)
        call.data = "1.2"
        call.from_user.id = 12345
        call.answer = AsyncMock()
        call.message = AsyncMock()
        call.message.answer = AsyncMock()
        return call

    @pytest.fixture
    async def mock_state(self):
        state = AsyncMock(spec=FSMContext)
        state.get_data = AsyncMock(return_value={
            'age': 25,
            'sex': 5,
            'growth': 175,
            'weight': 70.0,
            'activity': 1.2
        })
        state.update_data = AsyncMock()
        state.set_state = AsyncMock()
        state.set_state.return_value = None
        return state

    async def test_calorie_calculation_complete_flow(self, mock_call, mock_state):
        """Тестирует полный расчет калорий"""
        mock_call.data = "1.55"  # Умеренная активность

        with patch('src.bot.save_calorie_calculation') as mock_save:
            await set_activity(mock_call, mock_state)

            # Проверяем, что расчет был выполнен
            mock_call.message.answer.assert_called()
            mock_save.assert_called_once()

            # Проверяем, что данные сохранены
            mock_state.update_data.assert_called()

            # Проверяем, что состояние сброшено
            mock_state.set_state.assert_called_with(None)