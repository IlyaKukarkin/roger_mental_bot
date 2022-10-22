from aiogram import Bot, types
from aiogram.dispatcher.filters.state import State, StatesGroup

class Recording(StatesGroup):
    Name=State()
    AwaitForAName=State()
    AwaitForATimeZone=State()
    TimeToSend=State()
    AwaitForATimeToSend=State()
    AwaitForATimeZoneToSend = State()
    AwaitForAFeedback = State()