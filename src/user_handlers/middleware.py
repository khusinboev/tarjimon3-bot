from aiogram import Router, F
from aiogram.enums import ChatType, ChatAction
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

import asyncio
import logging

from src.buttons.function import Lang
from src.config import bot, sql, adminStart, db
from src.database.functions import Authenticator
from src.functions.functions import CheckData, PanelFunc
from src.buttons.buttons import UserPanels

router = Router()


# Tillarni tanlash bo'limi
@router.message(F.text == "✅Tillarni tanlash", lambda message: message.chat.type == ChatType.PRIVATE)
async def command_start_handler(message: Message) -> None:
    user_id = message.from_user.id
    await message.answer("Tillar / Languages", reply_markup=await UserPanels.langs_inline(user_id))

# Bazadan til kodlarini olish funksiyasi
def call_filter():
    sql.execute("SELECT lang_in FROM public.langs_list")
    lang_ins = [item[0] for item in sql.fetchall()]
    sql.execute("SELECT lang_out FROM public.langs_list")
    lang_outs = [item[0] for item in sql.fetchall()]
    lang_outs.append("TTS")
    return lang_ins + lang_outs

# Til kodlarini tekshirish handleri
@router.callback_query(F.data.in_(call_filter()))  # F.filteri ishlatiladi
async def check(call: CallbackQuery):
    user_id = call.from_user.id
    try:
        await call.answer()
    except Exception as e:
        logging.error(f"Callback answer error: {e}")

    try:
        await Lang.user_lang_check(call)
        await call.message.edit_reply_markup(reply_markup=await UserPanels.langs_inline(user_id))
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            logging.error(f"Error editing message: {e}")
    except Exception as e:
        await bot.send_message(chat_id=adminStart, text=f"Error in edit: \n\n{e}\n\n\n{call.from_user}")

# Til almashtirish handleri
@router.callback_query(F.data == "exchangeLang")  # F.filteri ishlatiladi
async def exchange_lang(call: CallbackQuery):
    user_id = call.from_user.id
    try:
        sql.execute(f"SELECT in_lang, out_lang FROM public.user_langs WHERE user_id='{user_id}'")
        codes = sql.fetchone()
        if codes:
            in_lang, out_lang = codes
            await call.answer(f"{out_lang} --> {in_lang}")
            sql.execute(f"UPDATE public.user_langs SET out_lang = '{in_lang}', in_lang = '{out_lang}' WHERE user_id='{user_id}'")
            db.commit()
    except Exception as e:
        logging.error(f"Error exchanging languages: {e}")
        await bot.send_message(chat_id=adminStart, text=f"Error in exchangeLang: \n\n{e}\n\n\n{call.from_user}")

# Til ro'yxatini ko'rsatish handleri
@router.callback_query(F.data == "lang_list")  # F.filteri ishlatiladi
async def show_lang_list(call: CallbackQuery):
    try:
        await call.answer()
        await bot.send_chat_action(chat_id=call.from_user.id, action=ChatAction.TYPING)  # ChatAction ishlatiladi
        await Authenticator.auth_user(call.message)
        await call.message.answer("Choose languages", reply_markup=await UserPanels.langs_inline(call.from_user.id))
    except Exception as e:
        logging.error(f"Error showing language list: {e}")
        await bot.send_message(chat_id=adminStart, text=f"Error in lang_list: \n\n{e}\n\n\n{call.from_user}")


# TIL SOZLAMALARI // TILLARNI BELGILASH
@router.message(F.text == "⚙️Tillarni sozlash", lambda message: message.chat.type == ChatType.PRIVATE)
async def lang_set(message: Message) -> None:
    user_id = message.from_user.id
    await message.answer("Tillar / Languages", reply_markup=await UserPanels.user_langs_inline(user_id))

def lang_filter():
    sql.execute(f"""select code from public.langs_list""")
    code = ["_" + str(item[0]) for item in sql.fetchall()]
    print(code)
    return code

# Til kodlarini tekshirish handleri
@router.callback_query(F.data.in_(lang_filter()))  # F.filteri ishlatiladi
async def check(call: CallbackQuery):
    await call.answer()
    print(call.data)
    user_id = call.from_user.id
    try:await call.answer()
    except: pass

    # try:
    await Lang.user_lang_update(call)
    await call.message.edit_reply_markup(reply_markup=await UserPanels.user_langs_inline(user_id))
    # except TelegramBadRequest as e:
    #     if "message is not modified" not in str(e):
    #         logging.error(f"Error editing message: {e}")
    # except Exception as e:
    #     await bot.send_message(chat_id=adminStart, text=f"Error in edit: \n\n{e}\n\n\n{call.from_user}")

@router.callback_query()  # F.filteri ishlatiladi
async def check(call: CallbackQuery):
    await call.answer()
