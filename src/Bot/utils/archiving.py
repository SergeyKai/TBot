import asyncio
import time

from aiogram import Bot
from aiogram.types import FSInputFile
from aiogram.utils.markdown import link

from aiohttp import ClientSession, ClientConnectorError
import shutil
import os
from io import BytesIO
from PIL import Image
import uuid
import yadisk

from Bot.config import BASE_DIR, Config


class Zip:
    def __init__(self, path: str, auto_delete_source: bool = False):
        """
        path:str: Путь к файлу или директории
        auto_delete_source:bool: . Если True - файл/директория будут автоматически удалена
        """
        self._root_path = path
        self.zip_file_path = self.get_zip()
        self.zip_file_name = self.zip_file_path.split('\\')[-1]
        self.zip_file_size = os.path.getsize(self.zip_file_path)

        if auto_delete_source:
            self._delete_source()

    def _delete_source(self):
        if os.path.isdir(self._root_path):
            shutil.rmtree(self._root_path)
        elif os.path.isfile(self._root_path):
            os.remove(self._root_path)

    def get_zip(self):
        """
        создает zip файл

        returne:str  Путь к созданному zip архиву
        """
        zip_path = shutil.make_archive(
            self._root_path,
            'zip',
            self._root_path,
        )
        return zip_path

    def set_remove_zip_task(self):
        """  """
        pass


async def download_images(img_urls: [str], dir_path: str) -> None:
    async with ClientSession() as session:
        for img_url in img_urls:
            try:
                async with session.get(img_url) as response:
                    if response.status == 200:
                        img = Image.open(BytesIO(await response.read()))
                        img.save(
                            os.path.join(
                                dir_path,
                                f'{str(uuid.uuid4())}.jpg'
                            )
                        )
            except ClientConnectorError:
                pass


def create_dir() -> str:
    """
    создает директорию с уникальным именем

    return:str возвращает путь к созданной директории
    """
    dir_path = os.path.join(
        BASE_DIR,
        str(uuid.uuid4())
    )
    os.mkdir(dir_path)
    return dir_path


def cloud_upload(file_path: str, file_name: str) -> str:
    """
    Загружает файл в облако

    file_path:str : локальный путь к файлу
    file_name:str : имя файла на облаке
    """
    cloud_instance = yadisk.YaDisk(token=Config.YANDEX_TOKEN)
    cloud_instance.upload(file_path, file_name)
    cloud_instance.publish(file_name)
    response = cloud_instance.get_meta(file_name)
    return response.file


async def zip_parse(img_urls: list, user_id: int, bot: Bot):
    dir_path = create_dir()
    await download_images(img_urls, dir_path)
    zip_file = Zip(dir_path)

    if zip_file.zip_file_size < 50 * 1024 * 1024:
        await bot.send_document(user_id, FSInputFile(zip_file.zip_file_path))
    else:
        zip_link = cloud_upload(zip_file.zip_file_path, zip_file.zip_file_name)
        await bot.send_message(user_id, link('file', zip_link))
