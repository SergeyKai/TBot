import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from dataclasses import dataclass

load_dotenv(find_dotenv())

BASE_DIR = Path(__file__).parent.parent


@dataclass
class RedisConfig:
    HOST: str
    PORT: int
    DB: int
    DECODE_RESPONSE: bool = True

    def get_url(self):
        return f'redis://{self.HOST}:{self.PORT}/{self.DB}'


@dataclass
class TaskConfig:
    trigger: str = 'interval'
    # interval: int = 60
    interval: int = 60 * 10

    count_of_posts = 100


@dataclass
class Config:
    BOT_TOKEN: str = os.getenv('TOKEN')
    ADMIN_ID: int = int(os.getenv('ADMIN_ID'))
    YANDEX_TOKEN: str = os.getenv('YANDEX_TOKEN')

    VK_ACCESS_TOKEN = os.getenv('VK_SERVICES_ACCESS_KEY')

    DB_URL = f'sqlite+aiosqlite:///{BASE_DIR}/Bot/db/db.sqlite3'

    REDIS_CONFIG = RedisConfig(
        HOST='localhost',
        PORT=6379,
        DB=0,
    )
