from aiogram.dispatcher.filters.state import State, StatesGroup

class Recording(StatesGroup):
    Name = State()
    AwaitForAName = State()
    AwaitForATimeZone = State()
    TimeToSend = State()
    AwaitForATimeToSend = State()
    AwaitForARateStata = State()
    AwaitForATimeZoneToSend = State()
    AwaitForAFeedback = State()
    AwaitForAMessageForAll = State()
    AwaitForAnAnswerToFeedback = State()
    AwaitForAProblem = State()

