from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from aiogram.types.dice import Dice

from Bot.config import Config
from Bot.keyboards import MainKeyboard, cancel_kb, ParseInlineKeyboard
from Bot.states import ParsingStates
from Bot.utils import check_vk_group
from Bot.utils.archiving import zip_parse, zip_parse
from src.Bot.comands import Commands
from src.Bot.resource import text

from Bot.utils.vk_api import parse, get_only_images

router = Router()


def data_group_response_message(group):
    formatted_text = f'`{group["name"]}`'
    photo = group['photo_200']
    return photo, formatted_text


@router.message(F.text == MainKeyboard().PARS_BTN.text)
async def start_parse(message: Message, state: FSMContext):
    await message.answer(text.GET_GROUP_TEXT, reply_markup=cancel_kb)
    await message.answer_dice()
    await state.set_state(ParsingStates.GET_GROUP)


@router.message(ParsingStates.GET_GROUP)
async def get_group(message: Message, state: FSMContext):
    domain = message.text.split('/')[-1]
    group = await check_vk_group(Config.VK_ACCESS_TOKEN, domain)
    if group:
        if group['is_closed'] == 1:
            await message.answer(text.CLOSED_GROUP_TEXT)
        else:
            await state.update_data(group=group)
            await state.set_state(ParsingStates.GET_COUNT_OF_POSTS)
            await message.answer(text.GET_COUNT_OF_POSTS_TEXT)
    else:
        await message.answer(text.INCORRECT_GROUP_TEXT)


@router.message(ParsingStates.GET_COUNT_OF_POSTS)
async def get_count_of_posts(message: Message, state: FSMContext):
    try:
        count_of_posts = int(message.text)
        await state.update_data(count_of_posts=count_of_posts)
        await message.answer_photo(
            *data_group_response_message((await state.get_data())['group']),
            reply_markup=ParseInlineKeyboard().get_keyboard()
        )
    except ValueError:
        await message.answer(text.INCORRECT_COUNT_OF_POSTS)


@router.callback_query(
    ParsingStates.GET_COUNT_OF_POSTS,
    F.data == ParseInlineKeyboard().PARSE_BTN.callback_data,
)
async def run_parsing(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer(text.PARSING_PROCESS)
    await state.set_state(ParsingStates.PARSING_PROCESS)
    data = await state.get_data()
    await parse(
        chat_id=callback.from_user.id,
        tg_bot=bot,
        domain=data['group']['screen_name'],
        state=state,
        count_of_posts=int(data['count_of_posts'])
    )


@router.callback_query(
    ParsingStates.GET_COUNT_OF_POSTS,
    F.data == ParseInlineKeyboard().PARSE_TO_ZIP_BTN.callback_data,
)
async def run_parsing_to_zip(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer(text.PARSING_PROCESS)
    await state.set_state(ParsingStates.PARSING_PROCESS)
    data = await state.get_data()
    post_images = await get_only_images(
        domain=data['group']['screen_name'],
        count_of_posts=int(data['count_of_posts'])
    )

    await zip_parse(post_images, callback.from_user.id, bot)

    # zip_file_path = await get_zip(post_images)

    # await callback.message.answer_document(
    #     FSInputFile(zip_file_path)
    # )
    # await remove_zip(zip_file_path)
