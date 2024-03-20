from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from Bot.admin.comands import Commands
from Bot.config import Config
from Bot.db.managers import TgChannelManager
from src.Bot.admin.keyboards import AdminPanelKeyboard, AdminTgConsoleKeyboard, AdminTgSelectiveModeKeyboard
from src.Bot.admin.resource import text
from src.Bot.admin import AdminCommands

from src.Bot.filters import IsAdmin
from src.Bot.comands import Commands as BotCommands

router = Router()


@router.channel_post(
    F.chat.type == 'channel',
    Command(Commands.SAVE_CHANNEL_IN_DB.command),
)
async def save_channel(message: Message, bot: Bot):
    chant = message.chat
    try:
        await TgChannelManager().create(
            tg_id=chant.id,
            name=chant.title,
        )
    except Exception as e:
        print(e)
        return
    await message.delete()
    await bot.send_message(chat_id=Config.ADMIN_ID, text=f'`Channel {chant.title} {chant.id} added to db`')


@router.message(F.text == AdminPanelKeyboard().TG_CONSOLE_BTN.text)
async def vk_console(message: Message):
    await message.answer(text.TG_CONSOLE, reply_markup=AdminTgConsoleKeyboard().get_keyboard())


@router.message(F.text == AdminTgConsoleKeyboard().CHANNEL_LIST_BTN.text)
async def channel_list(message: Message):
    channels = await TgChannelManager().get_all()
    for channel in channels:
        await message.answer(str(channel))


@router.message(F.text == AdminTgConsoleKeyboard().SELECTIVE_MOD_BTN.text)
async def selective_mode(message: Message):
    channels = await TgChannelManager().get_all()
    for channel in channels:
        await message.answer(str(channel), reply_markup=AdminTgSelectiveModeKeyboard().get_keyboard(channel.id))


@router.callback_query(F.data.startswith(AdminTgSelectiveModeKeyboard().DELETE_BTN.callback_data))
async def delete_channel_from_db(callback: CallbackQuery):
    channel_id = callback.data.split('_')[-1]

    tg_db_manager = TgChannelManager()
    channel = await tg_db_manager.get_by_id(int(channel_id))

    await tg_db_manager.delete(channel)
    await callback.answer(text.SUCCESS)
