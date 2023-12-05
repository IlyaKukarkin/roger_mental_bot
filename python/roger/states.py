"""Module with Bot states."""

from aiogram.dispatcher.filters.state import State, StatesGroup


class Recording(StatesGroup):
    """Class representing a /support states"""

    AwaitForARateStata = State()
    AwaitForAFeedback = State()
    AwaitForAMessageForAll = State()
    AwaitForAnAnswerToFeedback = State()
    AwaitForAProblem = State()
    AwaitForAFriendContact = State()


class FriendsStates(StatesGroup):
    """Class representing a /friends states"""

    AwaitForAFriendNicknameToAdd = State()


class Registration(StatesGroup):
    """Class representing a "Registration" states"""

    Name = State()
    AwaitForAName = State()
    AwaitForATimeZone = State()
    AwaitForATimeZoneToSend = State()
    TimeToSend = State()
    AwaitForATimeToSend = State()
