from aiogram.filters import BaseFilter
from aiogram.types import Message

from src.Bot.config import Config


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message, *args, **kwargs):
        return message.from_user.id == Config.ADMIN_ID
