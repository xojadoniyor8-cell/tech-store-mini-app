import os
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛍 Texnika katalogini ochish",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ],
            [
                InlineKeyboardButton(
                    text="📞 Telefon qilish",
                    url="tel:+998XXXXXXXXX"
                )
            ]
        ]
    )

    await message.answer(
        "Assalomu alaykum! 👋\n\n"
        "Tech Store'ga xush kelibsiz! 🛍\n\n"
        "📱 Telefonlar\n"
        "💻 Noutbuklar\n"
        "📺 Televizorlar\n"
        "🏠 Maishiy texnika\n\n"
        "Kerakli texnikani katalogdan ko‘rishingiz mumkin.",
        reply_markup=keyboard
    )


@dp.message()
async def other_messages(message: types.Message):
    await message.answer(
        "Savolingizni yozing. 🤖\n\n"
        "Texnika haqida ma'lumot olish uchun savolingizni yuboring."
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
