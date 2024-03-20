import json

from aiogram.fsm.context import FSMContext
from aiogram import Bot
from aiogram.utils.media_group import MediaGroupBuilder

from Bot.tasks.storage import posts_storage
from src.Bot.config import Config
from src.Bot.resource import text
from src.Bot.states import ParsingStates
from src.Bot.vk_api.base import Wall, Groups, Bot as Vkbot


async def check_vk_group(vk_bot_token: str, domain: str):
    vk_bot = Vkbot(vk_bot_token)
    try:
        response = await Groups(vk_bot).get_by_id(domain)
        return False if 'error' in response else response['response'][0]
    finally:
        await vk_bot.close_session()


def get_current_size_photo(images: list):
    current_img = ''
    img_size = 0
    for img in images:
        if img_size < img['height'] + img['width']:
            img_size = img['height'] + img['width']
            current_img = img['url']
    return current_img


async def get_only_images(
        domain: str,
        count_of_posts: int,
        offset: int = 0,
        vk_bot_token: str = Config.VK_ACCESS_TOKEN):
    vk_bot = Vkbot(vk_bot_token)
    try:
        post_images = []
        response = await Wall(vk_bot).get_posts(domain, count_of_posts, offset=offset)
        for post in response:
            try:
                if post['marked_as_ads'] == 1:
                    continue
                for attachment in post['attachments']:
                    if attachment['type'] == 'photo':
                        img = get_current_size_photo(attachment['photo']['sizes'])
                        post_images.append(img) if img != '' else None
            except TypeError as e:
                print(e)
        return post_images
    finally:
        await vk_bot.close_session()


async def get_posts(vk_bot_token: str, domain: str, count_of_posts: int, offset: int = 0):
    vk_bot = Vkbot(vk_bot_token)
    try:
        posts = []
        response = await Wall(vk_bot).get_posts(domain, count_of_posts, offset=offset)
        for post in response:
            try:
                if post['marked_as_ads'] == 1:
                    continue
                post_data = {
                    'text': post['text'],
                    'id': post['id'],
                    'likes': post['likes']['count'],
                    'attachments': []
                }
                for attachment in post['attachments']:
                    if attachment['type'] == 'photo':
                        img = get_current_size_photo(attachment['photo']['sizes'])
                        post_data['attachments'].append(img) if img != '' else None
                posts.append(post_data)
            except TypeError as e:
                print(e)
        return posts
    finally:
        await vk_bot.close_session()


async def parse(chat_id: int, state: FSMContext, domain: str, count_of_posts: int, tg_bot: Bot,
                vk_bot_token: str = Config.VK_ACCESS_TOKEN):
    posts = await get_posts(vk_bot_token=vk_bot_token, domain=domain, count_of_posts=count_of_posts)
    for post in posts:
        if await state.get_state() == ParsingStates.PARSING_PROCESS:
            group_post_images = MediaGroupBuilder()
            if len(post['attachments']) > 0:
                for image in post['attachments']:
                    group_post_images.add_photo(media=image)
                await tg_bot.send_media_group(chat_id=chat_id, media=group_post_images.build())
            else:
                pass
        else:
            break
    await tg_bot.send_message(chat_id=chat_id, text=text.PARSING_COMPLETE)
    await state.clear()
