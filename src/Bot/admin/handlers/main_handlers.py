from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src.Bot.admin.keyboards import AdminPanelKeyboard, AdminBotConfigKeyboard
from src.Bot.admin.resource import text
from src.Bot.admin import AdminCommands
from src.Bot.tasks.manager import scheduler

from src.Bot.filters import IsAdmin
from src.Bot.comands import Commands as BotCommands

router = Router()


@router.message(Command(BotCommands.CANCEL_COMMAND.command))
@router.message(F.text == 'cancel')
@router.callback_query(F.data == '_cancel_')
async def cancel_handler(ctx: Message | CallbackQuery, state: FSMContext):
    await state.clear()
    await ctx.answer(text=text.CANCEL_TEXT)


@router.message(IsAdmin(), Command(AdminCommands.ADMIN_PANEL.command))
async def show_admin_panel(message: Message):
    await message.answer(text.ADMIN_PANEL_TEXT, reply_markup=AdminPanelKeyboard().get_keyboard())


@router.message(IsAdmin(), F.text == AdminPanelKeyboard().BOT_CONFIG_BTN.text)
async def bot_config_panel(message: Message):
    await message.answer(text.BOT_CONFIG_CONSOLE, reply_markup=AdminBotConfigKeyboard().get_keyboard())


@router.message(IsAdmin(), F.text == AdminBotConfigKeyboard().START_SCHEDULER_BTN.text)
async def start_shed(message: Message):
    scheduler.start()
    await message.answer(text.START_SCHEDULER)


@router.message(IsAdmin(), F.text == AdminBotConfigKeyboard().SHUTDOWN_SCHEDULER_BTN.text)
async def shutdown_shed(message: Message):
    scheduler.shutdown(wait=True)
    await message.answer(text.SHUTDOWN_SCHEDULER)


@router.message(IsAdmin(), F.text == AdminBotConfigKeyboard().REMOVE_ALL_JOBS_SCHEDULER_BTN.text)
async def remove_all_jobs_shed(message: Message):
    scheduler.remove_all_jobs()
    await message.answer(text.REMOVE_ALL_JOBS_SCHEDULER)


@router.message(IsAdmin(), F.text == AdminBotConfigKeyboard().JOBS_LIST_SCHEDULER_BTN.text)
async def jobs_list_shed(message: Message):
    print(scheduler.get_jobs())
    print(scheduler)
    jobs = scheduler.get_jobs()
    if jobs:
        for job in scheduler.get_jobs():
            await message.answer(f'`{job}`')
    else:
        await message.answer(text.EMPTY_JOB_LIST)
