from aiogram import Dispatcher

from .check_subscription import CheckSubscription


def setup(dp: Dispatcher):
    dp.middleware.setup(CheckSubscription())