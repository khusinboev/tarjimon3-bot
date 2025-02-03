from aiogram import Router
from aiogram.enums import ChatAction
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatAction, ChatType

from src.config import bot, sql, adminStart
from src.database.functions import Authenticator
from src.functions.functions import CheckData
from src.buttons.buttons import LanguageInline

router = Router()


@router.message(CommandStart(), lambda message: message.chat.type == ChatType.PRIVATE)
async def command_start_handler(message: Message) -> None:
    user_id = message.from_user.id
    await message.answer("boshlanishi")
