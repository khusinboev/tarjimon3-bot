from aiogram import Router, F
from aiogram.enums import ChatType, ChatAction
from aiogram.types import Message, CallbackQuery

from src.buttons.function import Lang
from config import bot, sql, adminStart, db
from src.database.functions import Authenticator
from src.buttons.buttons import UserPanels

router = Router()


# Tillarni tanlash bo'limi
@router.message(F.text == "✅Tillarni tanlash", lambda message: message.chat.type == ChatType.PRIVATE)
async def command_start_handler(message: Message) -> None:
    user_id = message.from_user.id
    await message.answer("Tillar / Languages", reply_markup=await UserPanels.langs_inline(user_id))

# Bazadan til kodlarini olish funksiyasi
def call_filter():
    sql.execute("SELECT lang_in FROM langs_list")
    lang_ins = [item[0] for item in sql.fetchall()]
    sql.execute("SELECT lang_out FROM langs_list")
    lang_outs = [item[0] for item in sql.fetchall()]
    lang_outs.append("TTS")
    return lang_ins + lang_outs

# Til kodlarini tekshirish handleri
@router.callback_query(F.data.in_(call_filter()))  # F.filteri ishlatiladi
async def check(call: CallbackQuery):
    user_id = call.from_user.id
    try:await call.answer()
    except: pass

    try:
        await Lang.user_lang_check(call)
        await call.message.edit_reply_markup(reply_markup=await UserPanels.langs_inline(user_id))
    except Exception as e:
        pass
        # await bot.send_message(chat_id=adminStart, text=f"Error in edit: \n\n{e}\n\n\n{call.from_user}")

# Til almashtirish handleri
@router.callback_query(F.data == "exchangeLang")  # F.filteri ishlatiladi
async def exchange_lang(call: CallbackQuery):
    user_id = call.from_user.id
    sql.execute(f"SELECT in_lang, out_lang FROM user_langs WHERE user_id='{user_id}'")
    try:
        codes = sql.fetchone()
        if codes:
            in_lang, out_lang = codes
            sql.execute(f"UPDATE user_langs SET out_lang = '{in_lang}', in_lang = '{out_lang}' WHERE user_id='{user_id}'")
            await call.answer(f"{out_lang} --> {in_lang}")
            db.commit()
    except Exception as e:
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
        await bot.send_message(chat_id=adminStart, text=f"Error in lang_list: \n\n{e}\n\n\n{call.from_user}")


# TIL SOZLAMALARI // TILLARNI BELGILASH
@router.message(F.text == "⚙️Tillarni sozlash", lambda message: message.chat.type == ChatType.PRIVATE)
async def lang_set(message: Message) -> None:
    user_id = message.from_user.id
    await message.answer("Tillar / Languages", reply_markup=await UserPanels.user_langs_inline(user_id))


# TIL SOZLAMALARI // TILLARNI BELGILASH
@router.message(F.text == "📑Yo'riqnoma", lambda message: message.chat.type == ChatType.PRIVATE)
async def lang_set(message: Message) -> None:
    user_id = message.from_user.id
    await bot.copy_message(chat_id=user_id, from_chat_id=-1002499471134, message_id=2)


# TIL SOZLAMALARI // TILLARNI BELGILASH
@router.message(F.text == "️‼️Fikr bildirish", lambda message: message.chat.type == ChatType.PRIVATE)
async def lang_set(message: Message) -> None:
    user_id = message.from_user.id
    await message.answer(text="https://t.me/translate_bot_chat")


def lang_filter():
    sql.execute(f"""select code from langs_list""")
    code = ["_" + str(item[0]) for item in sql.fetchall()]
    return code

# Til kodlarini tekshirish handleri
@router.callback_query(F.data.in_(lang_filter()))  # F.filteri ishlatiladi
async def check(call: CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    try:await call.answer()
    except: pass
    await Lang.user_lang_update(call)
    try:await call.message.edit_reply_markup(reply_markup=await UserPanels.user_langs_inline(user_id))
    except:pass


# @router.callback_query()  # F.filteri ishlatiladi
# async def check(call: CallbackQuery):
#     await call.answer()
#     print(call.data)