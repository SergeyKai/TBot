import aiohttp


class Bot:
    def __init__(self, access_token: str):
        self.__access_token = access_token
        self.__session = aiohttp.ClientSession()

    def create_new_session(self):
        self.__session = aiohttp.ClientSession()

    def get_token(self):
        return self.__access_token

    def get_session(self):
        return self.__session

    async def close_session(self):
        await self.__session.close()


class MethodManager:
    def __init__(self, bot: Bot, version_api: int = 5.131):
        self._base_url = 'https://api.vk.com/method'
        self._session = bot.get_session()
        self._version_api = version_api
        self._bot = bot

    def get_params(self):
        return {
            'v': self._version_api,
            'access_token': self._bot.get_token()
        }

    async def get_request(self, method: str, **kwargs):
        url = f'{self._base_url}/{method}'
        params = self.get_params()
        params.update(kwargs)

        async with self._session.get(url, params=params) as response:
            return await response.json()


class Wall(MethodManager):
    async def get_posts(self, group: str | int, count_of_posts: int = 100, offset: int = 0):
        posts = []
        if count_of_posts <= 100:
            response = await super().get_request(
                'wall.get',
                domain=group,
                count=count_of_posts,
                offset=offset,
            )
            try:
                posts.extend(response['response']['items'])
            except KeyError:
                return response
        else:
            while count_of_posts > 0:
                response = await super().get_request(
                    'wall.get',
                    domain=group,
                    count=count_of_posts if count_of_posts < 100 else 100,
                    offset=offset,
                )
                posts.extend(response['response']['items'])
                count_of_posts -= 100
                offset += 100
        return posts


class Groups(MethodManager):
    async def get_by_id(self, group_ids: str | list):
        if type(group_ids) == str:
            group_ids = [group_ids]

        response = await super().get_request(
            'groups.getById',
            group_ids=' , '.join(group_ids)
        )

        return response
