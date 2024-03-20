from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy import ForeignKey, String, BigInteger, Table, Column


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class User(Base):
    __tablename__ = 'users'
    username: Mapped[str]
    tg_id: Mapped[int] = mapped_column(unique=True)

    is_admin: Mapped[bool] = mapped_column(default=False)

    def __repr__(self):
        return f'{self.__class__.__name__}\n' \
               f'username: {self.username}\n' \
               f'tg_id:{self.tg_id}'


tg_channel_vk_group_association_table = Table(
    'tg_channel_vk_group_association',
    Base.metadata,
    Column('tg_channel_id', ForeignKey('tg_channels.id'), primary_key=True),
    Column('vk_group_id', ForeignKey('vk_groups.id'), primary_key=True),
)


class TgChannel(Base):
    __tablename__ = 'tg_channels'

    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    name: Mapped[str]

    vk_groups: Mapped[list['VkGroup']] = relationship(
        secondary=tg_channel_vk_group_association_table,
        back_populates='tg_channels'
    )

    def __repr__(self):
        return f'`{self.__class__.__name__}\n' \
               f'tg_id: {self.tg_id}\n' \
               f'name: {self.name}`'


class VkGroup(Base):
    __tablename__ = 'vk_groups'

    vk_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    domain: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    is_closed: Mapped[bool]
    image: Mapped[str]

    tg_channels: Mapped[list['TgChannel']] = relationship(
        secondary=tg_channel_vk_group_association_table,
        back_populates='vk_groups'
    )

    def __repr__(self):
        return f'`{self.__class__.__name__}\n' \
               f'id: {self.id}\n' \
               f'vk_id: {self.vk_id}\n' \
               f'domain: {self.domain}\n' \
               f'name: {self.name}`\n'

    def msg_repr(self):
        formatted_text = f'`{self.name}\n' \
                         f'id: {self.vk_id}\n' \
                         f'domain: {self.domain}`'
        return self.image, formatted_text


class VkPost(Base):
    __tablename__ = 'vk_posts'

    vk_post_id: Mapped[int] = mapped_column(BigInteger, unique=True)

    def __repr__(self):
        return f'{self.__class__.__name__}\n' \
               f'vk_post_id: {self.vk_post_id}'
