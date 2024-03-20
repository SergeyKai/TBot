import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import selectinload

from Bot.config import Config
from .models import VkGroup, TgChannel, Base, VkPost


class SessionFactory:
    CONN_URL = Config.DB_URL

    def __init__(self):
        self.engine = create_async_engine(self.CONN_URL, echo=True)
        self.session = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )


class BaseManager:
    model = None

    def __init__(self):
        pass

    async def get_all(self):
        async with SessionFactory().session() as session:
            stmt = select(self.model)
            result = await session.scalars(stmt)
            return result.all()

    async def get_by_id(self, pk: int) -> model:
        async with SessionFactory().session() as session:
            stmt = select(self.model).where(self.model.id == pk)
            return await session.scalar(stmt)

    async def create(self, **kwargs) -> model:
        async with SessionFactory().session() as session:
            obj = self.model(**kwargs)
            session.add(obj)
            await session.commit()
            return obj

    async def update(self, obj) -> model:
        async with SessionFactory().session() as session:
            session.add(obj)
            await session.commit()
            return obj

    async def delete(self, obj):
        async with SessionFactory().session() as session:
            await session.delete(obj)
            await session.commit()
            return obj


class VkGroupManager(BaseManager):
    model = VkGroup

    async def link_with_tg_channel(self, vk_group_id: int, tg_channel_id: int):
        async with SessionFactory().session() as session:
            tg_channel = await session.scalar(
                select(TgChannel)
                .where(TgChannel.tg_id == tg_channel_id)
            )
            vk_group = await session.scalar(
                select(self.model)
                .where(self.model.id == vk_group_id)
                .options(
                    selectinload(self.model.tg_channels)
                )
            )
            vk_group.tg_channels.append(tg_channel)
            await session.commit()
            return vk_group

    async def get_tg_channels(self, group_id: int):
        async with SessionFactory().session() as session:
            vk_group = await session.scalar(
                select(self.model)
                .where(self.model.id == group_id)
                .options(
                    selectinload(self.model.tg_channels)
                )
            )
            return vk_group.tg_channels

    async def get_by_vk_id(self, vk_id: int) -> model:
        async with SessionFactory().session() as session:
            stmt = select(self.model).where(self.model.vk_id == vk_id)
            return await session.scalar(stmt)


class TgChannelManager(BaseManager):
    model = TgChannel

    async def get_by_tg_id(self, tg_id):
        async with SessionFactory().session() as session:
            stmt = select(self.model).where(self.model.tg_id == tg_id)
            return await session.scalar(stmt)


class VkPostManger(BaseManager):
    model = VkPost
