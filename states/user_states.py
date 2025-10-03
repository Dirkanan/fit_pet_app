from aiogram.fsm.state import State, StatesGroup

class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()
    sex = State()
    activity = State()

class RegistrationExercise(StatesGroup):
    name_exercise = State()
    working_weight = State()
    iteration = State()
    confirm_update = State()
