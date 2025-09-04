import os
import asyncio
import json
import logging
import sys


from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import (
    Table, Column, Integer, BigInteger, String, Text, TIMESTAMP, Boolean, JSON, MetaData,
    insert, func
)


logging.basicConfig(
    level=logging.INFO,  # INFO и ERROR
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


# --- Настройки из .env ---
DB_USER = os.getenv("POSTGRES_USER", "telegram_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "supersecret")
DB_NAME = os.getenv("POSTGRES_DB", "telegram")
DB_HOST = os.getenv("POSTGRES_HOST", "telegram-db")   # важно: внутри docker сети!
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
BOT_TOKEN = os.getenv("BOT_TOKEN")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# --- SQLAlchemy ---
metadata = MetaData()

messages = Table(
    "messages",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("chat_id", BigInteger, nullable=False),
    Column("chat_title", Text),
    Column("user_id", BigInteger),
    Column("username", String(255)),
    Column("first_name", String(255)),
    Column("last_name", String(255)),
    Column("language_code", String(10)),
    Column("message_type", String(50)),
    Column("text", Text),
    Column("media_file_id", String(255)),
    Column("has_media", Boolean, default=False),
    Column("is_forwarded", Boolean, default=False),
    Column("forward_from_user_id", BigInteger),
    Column("forward_from_chat_id", BigInteger),
    Column("forward_from_message_id", BigInteger),
    Column("reply_to_message_id", BigInteger),
    Column("thread_id", BigInteger),
    Column("raw_json", JSON),
    Column("date", TIMESTAMP, server_default=func.now()),
)

engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,
)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# --- Aiogram ---
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()


def json_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


@dp.message()
async def save_message(message: Message):
    async with async_session() as session:
        try:
            values = {
                "chat_id": message.chat.id,
                "chat_title": message.chat.title,
                "user_id": message.from_user.id if message.from_user else None,
                "username": message.from_user.username if message.from_user else None,
                "first_name": message.from_user.first_name if message.from_user else None,
                "last_name": message.from_user.last_name if message.from_user else None,
                "language_code": (
                    message.from_user.language_code
                    if message.from_user and message.from_user.language_code
                    else None
                ),
                "message_type": message.content_type,
                "text": message.text or message.caption,
                "media_file_id": None,
                "has_media": bool(
                    message.photo or message.video or message.document or message.voice or message.audio
                ),
                # ✅ aiogram v3: проверяем по полям
                "is_forwarded": bool(
                    message.forward_from
                    or message.forward_from_chat
                    or message.forward_sender_name
                ),
                "forward_from_user_id": message.forward_from.id if message.forward_from else None,
                "forward_from_chat_id": message.forward_from_chat.id if message.forward_from_chat else None,
                "forward_from_message_id": message.forward_from_message_id,
                "reply_to_message_id": (
                    message.reply_to_message.message_id if message.reply_to_message else None
                ),
                "thread_id": getattr(message, "message_thread_id", None),
                "raw_json": json.dumps(message.model_dump(), default=json_serializer),
            }

            if message.photo:
                values["media_file_id"] = message.photo[-1].file_id
            elif message.video:
                values["media_file_id"] = message.video.file_id
            elif message.document:
                values["media_file_id"] = message.document.file_id
            elif message.voice:
                values["media_file_id"] = message.voice.file_id
            elif message.audio:
                values["media_file_id"] = message.audio.file_id

            await session.execute(insert(messages).values(**values))
            await session.commit()
        except Exception as e:
            logger.error(f"Ошибка при сохранении сообщения: {e}", exc_info=True)

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
