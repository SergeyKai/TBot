from aiogram.fsm.state import StatesGroup, State


class AddGroupStates(StatesGroup):
    GET_GROUP = State()
    LINK_WITH_CHANNEL = State()


class SelectiveModeStates(StatesGroup):
    GET_COUNT_OF_POSTS = State()
    READY_TO_PARSE = State()
    PARSING_PROCESS = State()


class AdminParsingStates(StatesGroup):
    GET_GROUP = State()
    GET_COUNT_OF_POSTS = State()
    READY_TO_PARSE = State()
    PARSING_PROCESS = State()
