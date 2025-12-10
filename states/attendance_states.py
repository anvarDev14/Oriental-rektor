"""
Davomat tizimi uchun FSM States
"""
from aiogram.dispatcher.filters.state import State, StatesGroup


class StudentRegistration(StatesGroup):
    full_name = State()
    student_id = State()
    direction = State()
    group = State()
    phone = State()
    confirm = State()


class CreateSession(StatesGroup):
    direction = State()
    group = State()
    subject = State()
    duration = State()
    confirm = State()


class AddDirection(StatesGroup):
    name = State()


class AddGroup(StatesGroup):
    direction = State()
    name = State()


class ExportReport(StatesGroup):
    direction = State()
    group = State()
    date_range = State()
