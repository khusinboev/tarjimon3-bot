from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatAction, ChatType

from config import bot, sql, adminStart
from src.database.functions import Authenticator
from src.functions.functions import CheckData
from src.buttons.buttons import UserPanels

router = Router()


@router.message(CommandStart(), lambda message: message.chat.type == ChatType.PRIVATE)
async def command_start_handler(message: Message) -> None:
    user_id = message.from_user.id
    await bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)
    await Authenticator.auth_user(message)
    try:
        if await CheckData.check_member(bot, message.from_user.id):
            await message.answer(
                text="Xush kelibsiz\n\n\nWelcome to my bot", reply_markup=await UserPanels.main_manu())
        else:
            await message.answer(text="Botimizdan foydalanish uchun kanalimizga azo bo'ling"
                                      "\nSubscribe to our channel to use our bot",
                                 reply_markup=await UserPanels.join_btn(user_id))
    except Exception as ex:
        await bot.forward_message(chat_id=adminStart, from_chat_id=message.chat.id, message_id=message.message_id)
        await bot.send_message(chat_id=adminStart, text=f"Error in start: \n\n{ex}")


@router.callback_query(F.data == "check", F.message.chat.type == "private")
async def check(call: CallbackQuery):
    user_id = call.from_user.id
    try: await call.answer()
    except: pass
    try:
        if await CheckData.check_member(bot, user_id):
            await call.message.delete()
            await bot.send_message(chat_id=user_id, text="Choose languages", reply_markup=await UserPanels.main_manu())
        else:
            try:
                await call.answer(show_alert=True,
                              text="Botimizdan foydalanish uchun kanalimizga azo bo'ling"
                                   "\nSubscribe to our channel to use our bot")
            except:
                pass
    except Exception as e:
        await bot.forward_message(chat_id=adminStart, from_chat_id=call.message.chat.id, message_id=call.message.message_id)
        await bot.send_message(chat_id=adminStart, text=f"Error in check: \n\n{e}")
