import os
import asyncio
from aiogram import Bot, Dispatcher, types
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text as sql_text
from dotenv import load_dotenv

# Загружаем .env из папки выше
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@db:5432/postgres"
)

if not TOKEN:
    raise RuntimeError("❌ BOT_TOKEN не найден в .env")

bot = Bot(token=TOKEN)
dp = Dispatcher()
engine = create_async_engine(DATABASE_URL, echo=True)

# Инициализация БД
async def init_db():
    async with engine.begin() as conn:
        await conn.execute(sql_text("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            chat_id BIGINT NOT NULL,
            user_id BIGINT,
            username TEXT,
            text TEXT,
            date TIMESTAMP DEFAULT NOW()
        );
        """))

# Логируем ВСЕ сообщения в базу
@dp.message()
async def save_message(message: types.Message):
    async with engine.begin() as conn:
        await conn.execute(sql_text("""
            INSERT INTO messages (chat_id, user_id, username, text, date)
            VALUES (:chat_id, :user_id, :username, :text, NOW());
        """), {
            "chat_id": message.chat.id,
            "user_id": message.from_user.id if message.from_user else None,
            "username": message.from_user.username if message.from_user else None,
            "text": message.text
        })

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
