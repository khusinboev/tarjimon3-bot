import asyncio, os
import logging
import sys

from aiogram import Router
from aiogram.loggers import middlewares
from aiogram.types import *#ChatMemberUpdated, ChatMember,

from config import dp, bot, adminStart, BASE_DIR
from src.database.functions import create_all_base
from src.middleware.middleware import RegisterUserMiddleware
from src.user_handlers import start_handler, user_handler, tarjima, comunicate
from src.admin_handlers.message import msg_router
from src.admin_handlers import panel

router = Router()


async def on_startup() -> None:
    logging.info("Bot muvaffaqiyatli ishga tushirildi.")
    await bot.send_message(chat_id=adminStart, text="Successful. Bot started!")
    if not os.path.exists(BASE_DIR + "Audios"):
        os.makedirs(BASE_DIR + "Audios")
    if not os.path.exists(BASE_DIR + "photos"):
        os.makedirs(BASE_DIR + "photos")
    if not os.path.exists(BASE_DIR + "audio_tr"):
        os.makedirs(BASE_DIR + "audio_tr")
    await create_all_base()


async def main() -> None:
    dp.update.middleware(RegisterUserMiddleware())
    # Startup
    await on_startup()

    # Routerlar
    dp.include_router(router)
    dp.include_router(start_handler.router)
    dp.include_router(panel.admin_router)
    dp.include_router(msg_router)
    # dp.include_router(comunicate.router)
    dp.include_router(user_handler.router)
    dp.include_router(tarjima.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())