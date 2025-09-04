import json
import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

# Загружаем .env из папки уровнем выше
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в .env")

# aiogram 3.7+: parse_mode через DefaultBotProperties
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher()


@dp.message()
async def handle_message(message: types.Message):
    # Печатаем апдейт в JSON
    print(json.dumps(message.model_dump(), ensure_ascii=False, indent=2))


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
