from aiogram.dispatcher.filters.state import State, StatesGroup

class Recording(StatesGroup):
    AwaitForARateStata = State()
    AwaitForAFeedback = State()
    AwaitForAMessageForAll = State()
    AwaitForAnAnswerToFeedback = State()
    AwaitForAProblem = State()

class FriendsStates(StatesGroup):    
    AwaitForAFriendNicknameToAdd = State()

class Registration(StatesGroup):
    Name = State()
    AwaitForAName = State()
    AwaitForATimeZone = State()
    AwaitForATimeZoneToSend = State()
    TimeToSend = State()
    AwaitForATimeToSend = State()

