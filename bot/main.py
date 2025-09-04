# bot/main.py
# Бот на aiogram 3.x: принимает любые сообщения в группах и пишет их в Postgres


import os
from datetime import timezone

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ChatType, ContentType


from sqlalchemy import select, insert, update
from sqlalchemy.exc import IntegrityError


from app_common.db import engine, AsyncSessionLocal
from app_common.models import Base, DbMessage




BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Переменная окружения BOT_TOKEN не задана")


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()




async def init_db() -> None:
    """Создать таблицы, если их еще нет."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)




# Вспомогательная функция: аккуратно достаём строковые поля


def _safe(x):
    return x if x is not None else None




# Определяем тип медиа, если оно есть


def _detect_media_type(m: Message) -> tuple[bool, str | None]:
    # Проверяем самые частые типы
    if m.content_type in {
        ContentType.PHOTO,
        ContentType.VIDEO,
        ContentType.AUDIO,
        ContentType.VOICE,
        ContentType.DOCUMENT,
        ContentType.STICKER,
        ContentType.VIDEO_NOTE,
        ContentType.CONTACT,
        ContentType.LOCATION,
        ContentType.ANIMATION,
    }:
        return True, m.content_type
    return False, None




@dp.message() # ловим любые сообщения
async def on_message(message: Message) -> None:
    # Игнорируем личные чаты — проект про группы/супергруппы
    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        return
    has_media, media_type = _detect_media_type(message)

    # В aiogram 3.x объекты — это Pydantic-модели,