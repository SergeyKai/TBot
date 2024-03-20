from aiogram.types import (ReplyKeyboardMarkup,
                           KeyboardButton,
                           InlineKeyboardMarkup,
                           InlineKeyboardButton)

cancel_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text='CANCEL')]
    ]
)


class MainKeyboard:
    def __init__(self):
        self.PARS_BTN = KeyboardButton(text='Parse')

    def get_keyboard(self):
        return ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [self.PARS_BTN]
            ]
        )


class ParseInlineKeyboard:
    def __init__(self):
        self.PARSE_BTN = InlineKeyboardButton(text='PARS', callback_data='_parse_')
        self.PARSE_TO_ZIP_BTN = InlineKeyboardButton(text='Get Zip', callback_data='_get_zip_')
        self.CANCEL_BTN = InlineKeyboardButton(text='CANCEL', callback_data='_cancel_')

    def get_keyboard(self):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [self.PARSE_BTN],
                [self.PARSE_TO_ZIP_BTN],
                [self.CANCEL_BTN],
            ])
        return keyboard
