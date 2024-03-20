from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat

from src.Bot.config import Config


class Commands:
    ADMIN_PANEL = BotCommand(command='admin', description='Вызов панели администратора')
    SHOW_ACTIVE_TASKS = BotCommand(command='show_tasks', description='Выводит список текущих задач')
    SAVE_CHANNEL_IN_DB = BotCommand(command='save_channel', description='Добавить текущий канал в базу данных')

    @classmethod
    async def get_commands(cls):
        class_attributes = vars(cls)
        commands_list = [command for key, command in class_attributes.items() if
                         not key.startswith('_') and key.isupper()]
        return commands_list

    @classmethod
    async def set_commands(cls, bot: Bot):
        commands = await cls.get_commands()
        await bot.set_my_commands(await cls.get_commands(), BotCommandScopeChat(chat_id=Config.ADMIN_ID))
