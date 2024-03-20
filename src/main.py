import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from Bot.config import Config
from Bot.comands import Commands
from Bot.admin import AdminCommands

from Bot.tasks.manager import scheduler
from Bot.admin.handlers import admin_router
from Bot.handlers import main_router


async def bot_start(bot: Bot) -> None:
    await Commands.set_commands(bot)
    await AdminCommands.set_commands(bot)

    scheduler.start()

    await bot.send_message(Config.ADMIN_ID, text='Bot is running')


async def bot_stop(bot: Bot) -> None:
    await bot.send_message(Config.ADMIN_ID, text='Bot is stopped')
    # scheduler.remove_all_jobs()
    # scheduler.shutdown()


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    bot = Bot(Config.BOT_TOKEN, parse_mode=ParseMode.MARKDOWN_V2)

    storage = RedisStorage.from_url(Config.REDIS_CONFIG.get_url())
    dp = Dispatcher(storage=storage)

    scheduler.ctx.add_instance(bot, declared_class=Bot)

    dp.startup.register(bot_start)
    dp.shutdown.register(bot_stop)

    dp.include_routers(admin_router, main_router)

    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
