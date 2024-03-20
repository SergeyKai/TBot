from aiogram.fsm.state import StatesGroup, State


class ParsingStates(StatesGroup):
    GET_GROUP = State()
    GET_COUNT_OF_POSTS = State()
    READY_TO_PARSE = State()
    PARSING_PROCESS = State()
