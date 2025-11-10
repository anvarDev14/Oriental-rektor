from aiogram.dispatcher.filters.state import StatesGroup, State


class MessageStates(StatesGroup):
    waiting_for_message = State()
    confirm_message = State()


class BroadcastStates(StatesGroup):
    waiting_for_content = State()
    waiting_for_time = State()
    confirm_broadcast = State()


class ChannelStates(StatesGroup):
    waiting_for_channel_id = State()
    waiting_for_channel_name = State()
    waiting_for_channel_url = State()
