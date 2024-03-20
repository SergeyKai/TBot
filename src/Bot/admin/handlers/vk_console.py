from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.exc import IntegrityError

from Bot.admin.states import AddGroupStates, SelectiveModeStates
from Bot.db.managers import VkGroupManager, TgChannelManager
from Bot.tasks.manager import VkGroupTaskManager
from src.Bot.admin.keyboards import AdminPanelKeyboard, AdminVkConsoleKeyboard, AdminParseInlineKeyboard, \
    AdminAddGroupInlineKeyboard, AdminSelectiveModeInlineKeyboard, get_admin_link_group_with_channel_keyboard
from src.Bot.admin.resource import text
from src.Bot.admin import AdminCommands
from src.Bot.config import Config

from src.Bot.filters import IsAdmin
from src.Bot.comands import Commands as BotCommands
from src.Bot.admin.states import AdminParsingStates
from src.Bot.utils import check_vk_group, parse as group_parsing

router = Router()


def data_group_response_message(group):
    formatted_text = f'`{group["name"]}`\n' \
                     f'id: {group["id"]}\n' \
                     f'domain: `{group["screen_name"]}`'
    photo = group['photo_200']
    return photo, formatted_text


@router.message(IsAdmin(), F.text == AdminPanelKeyboard().VK_CONSOLE_BTN.text)
async def vk_console(message: Message):
    await message.answer(text.VK_CONSOLE_TEXT, reply_markup=AdminVkConsoleKeyboard().get_keyboard())


@router.message(IsAdmin(), F.text == AdminVkConsoleKeyboard().FAST_PARSE_BTN.text)
async def parse_(message: Message, state: FSMContext):
    await message.answer(text.GET_GROUP_TEXT)
    await state.set_state(AdminParsingStates.GET_GROUP)


@router.message(IsAdmin(), AdminParsingStates.GET_GROUP)
async def get_group(message: Message, state: FSMContext):
    domain = message.text.split('/')[-1]
    group = await check_vk_group(Config.VK_ACCESS_TOKEN, domain)
    if group:
        if group['is_closed'] == 1:
            await message.answer(text.CLOSED_GROUP_TEXT)
        else:
            await state.update_data(group=group)
            await state.set_state(AdminParsingStates.GET_COUNT_OF_POSTS)
            await message.answer(text.GET_COUNT_OF_POSTS_TEXT)
    else:
        await message.answer(text.INCORRECT_GROUP_TEXT)


@router.message(IsAdmin(), AdminParsingStates.GET_COUNT_OF_POSTS)
async def get_count_of_posts(message: Message, state: FSMContext):
    try:
        count_of_posts = int(message.text)
        await state.update_data(count_of_posts=count_of_posts)
        await message.answer_photo(
            *data_group_response_message((await state.get_data())['group']),
            reply_markup=AdminParseInlineKeyboard().get_keyboard()
        )
    except ValueError:
        await message.answer(text.INCORRECT_COUNT_OF_POSTS)


@router.callback_query(
    AdminParsingStates.GET_COUNT_OF_POSTS,
    F.data == AdminParseInlineKeyboard().PARSE_BTN.callback_data,
)
async def run_parsing(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer(text.PARSING_PROCESS)
    await state.set_state(AdminParsingStates.PARSING_PROCESS)
    data = await state.get_data()
    await group_parsing(
        chat_id=callback.from_user.id,
        tg_bot=bot,
        domain=data['group']['screen_name'],
        state=state,
        count_of_posts=int(data['count_of_posts'])
    )


@router.message(IsAdmin(), F.text == AdminVkConsoleKeyboard().ADD_GROUP_BTN.text)
async def add_group(message: Message, state: FSMContext):
    await state.set_state(AddGroupStates.GET_GROUP)
    await message.answer(text.ADD_GROUP_GET_GROUP_LINK)


@router.message(IsAdmin(), AddGroupStates.GET_GROUP)
async def get_group(message: Message, state: FSMContext):
    domain = message.text.split('/')[-1]
    group = await check_vk_group(Config.VK_ACCESS_TOKEN, domain)
    if group:
        if group['is_closed'] == 1:
            await message.answer(text.CLOSED_GROUP_TEXT)
        else:
            await message.answer_photo(
                *data_group_response_message(group),
                reply_markup=AdminAddGroupInlineKeyboard().get_keyboard()
            )
            await state.update_data(group=group)


@router.callback_query(
    IsAdmin(),
    F.data == AdminAddGroupInlineKeyboard().SAVE_BTN.callback_data
)
async def save_group_channel(callback: CallbackQuery, state: FSMContext):
    manager = VkGroupManager()
    group = (await state.get_data()).get('group')
    await manager.create(
        vk_id=group['id'],
        domain=group['screen_name'],
        name=group['name'],
        is_closed=group['is_closed'],
        image=group['photo_200'],
    )
    await callback.answer(text.SUCCESS)
    await state.clear()


@router.message(IsAdmin(), F.text == AdminVkConsoleKeyboard().GROUP_LIST_BTN.text)
async def group_list(message: Message):
    manager = VkGroupManager()
    for group in await manager.get_all():
        print(group)
        await message.answer(str(group))


@router.message(IsAdmin(), F.text == AdminVkConsoleKeyboard().SELECTIVE_MODE_BTN.text)
async def selective_mode(message: Message, state: FSMContext):
    manager = VkGroupManager()
    for group in await manager.get_all():
        try:
            await message.answer_photo(
                *group.msg_repr(),
                reply_markup=AdminSelectiveModeInlineKeyboard().get_keyboard(group.id)
            )
        except Exception as e:
            print(e)
            await message.answer(f'`{group.name}`',
                                 reply_markup=AdminSelectiveModeInlineKeyboard().get_keyboard(group.id))


@router.callback_query(IsAdmin(), F.data.startswith(AdminSelectiveModeInlineKeyboard().DELETE_BTN.callback_data))
async def delete_group(callback: CallbackQuery):
    group_id = callback.data.split('_')[-1]
    manager = VkGroupManager()
    group = await manager.get_by_id(int(group_id))
    await manager.delete(group)
    await callback.answer(text.SUCCESS)


@router.callback_query(IsAdmin(), F.data.startswith(AdminSelectiveModeInlineKeyboard().PARS_BTN.callback_data))
async def selective_mode_parse(callback: CallbackQuery, state: FSMContext):
    group_id = callback.data.split('_')[-1]
    await state.update_data(group_id=group_id)
    await callback.message.answer(text.GET_COUNT_OF_POSTS_TEXT)
    await state.set_state(SelectiveModeStates.GET_COUNT_OF_POSTS)


@router.message(IsAdmin(), SelectiveModeStates.GET_COUNT_OF_POSTS)
async def selective_get_count_of_post(message: Message, state: FSMContext):
    try:
        count_of_posts = int(message.text)
    except ValueError:
        await message.answer(text.INCORRECT_COUNT_OF_POSTS)
        return
    manager = VkGroupManager()
    group = await manager.get_by_id(
        int((await state.get_data())['group_id'])
    )
    await state.update_data(count_of_posts=count_of_posts)
    await state.update_data(domain=group.domain)
    await message.answer_photo(
        *group.msg_repr(),
        reply_markup=AdminParseInlineKeyboard().get_keyboard()
    )
    await state.set_state(SelectiveModeStates.READY_TO_PARSE)


@router.callback_query(
    IsAdmin(),
    SelectiveModeStates.READY_TO_PARSE,
    F.data == AdminParseInlineKeyboard().PARSE_BTN.callback_data
)
async def selective_pars_run(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.message.answer(text.PARSING_PROCESS)
    await state.set_state(AdminParsingStates.PARSING_PROCESS)
    data = await state.get_data()
    await group_parsing(
        chat_id=callback.from_user.id,
        tg_bot=bot,
        domain=data['domain'],
        state=state,
        count_of_posts=int(data['count_of_posts'])
    )


@router.callback_query(IsAdmin(), F.data.startswith(AdminSelectiveModeInlineKeyboard().LINK_BTN.callback_data))
async def link_with_channel(callback: CallbackQuery, state: FSMContext):
    await callback.answer(text.LINK_GROUP_WITH_CHANNEL)
    await state.update_data(group_id=callback.data.split('_')[-1])
    await callback.message.answer(text.LINK_GROUP_WITH_CHANNEL)
    tg_manager = TgChannelManager()
    for channel in await tg_manager.get_all():
        await callback.message.answer(str(channel),
                                      reply_markup=get_admin_link_group_with_channel_keyboard(channel.tg_id))


@router.callback_query(IsAdmin(), F.data.startswith('_select_'))
async def link_channel(callback: CallbackQuery, state: FSMContext):
    group_id = (await state.get_data())['group_id']
    tg_id = callback.data.split('_')[-1]

    vk_manager = VkGroupManager()
    try:
        await vk_manager.link_with_tg_channel(int(group_id), int(tg_id))
    except IntegrityError:
        await callback.message.answer(text.CHANNEL_ALREADY_LINKED)
    await callback.answer(text.SUCCESS)


@router.callback_query(
    IsAdmin(),
    F.data.startswith(AdminSelectiveModeInlineKeyboard().SHOW_LINKED_CHANNELS_BTN.callback_data),
)
async def check_linked_channels(callback: CallbackQuery):
    group_id = callback.data.split('_')[-1]
    tg_channels = await VkGroupManager().get_tg_channels(int(group_id))
    for channel in tg_channels:
        await callback.message.answer(str(channel))


@router.callback_query(
    IsAdmin(),
    F.data.startswith(AdminSelectiveModeInlineKeyboard().ADD_JOBS_BTN.callback_data),
)
async def add_jobs(callback: CallbackQuery):
    group_id = callback.data.split('_')[-1]
    group = await VkGroupManager().get_by_id(int(group_id))
    task_manager = VkGroupTaskManager(group)
    await task_manager.create_post_tasks_for_all_channels()
    await callback.answer(text.SUCCESS)
