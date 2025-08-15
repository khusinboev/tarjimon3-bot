import asyncio
from pathlib import Path

import requests
from aiogram import Router, Bot, F
from aiogram.enums import ChatAction
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ContentType, FSInputFile
from aiogram.filters import Command
from pydub import AudioSegment
from gtts import gTTS
import speech_recognition as sr
import os

from soupsieve.util import lower

from src.buttons.buttons import UserPanels
from config import sql, adminPanel, adminStart, BASE_DIR
from src.database.functions import Authenticator, DefinitionEn
from src.functions.functions import CheckData

router = Router()


# Tarjima usullarini alohida funksiyalarga ajratish
def translate_with_deep_translator(text, lang_in, lang_out):
    try:
        from deep_translator import GoogleTranslator
        tr = GoogleTranslator(source=lang_in, target=lang_out)
        result_text = str(tr.translate(text=text))
        return [result_text[i:i+1000] for i in range(0, len(result_text), 1000)]
    except Exception as e:
        print(f"Deep Translator xatosi: {e}")
        return None

def translate_with_googletrans(text, lang_in, lang_out):
    try:
        from googletrans import Translator
        translator = Translator()
        translation = translator.translate(text, src=lang_in, dest=lang_out)
        result_text = translation.text
        return [result_text[i:i+1000] for i in range(0, len(result_text), 1000)]
    except Exception as e:
        print(f"Googletrans xatosi: {e}")
        return None

def translate_with_mymemory(text, lang_in, lang_out):
    try:
        url = "https://api.mymemory.translated.net/get"
        params = {
            "q": text,
            "langpair": f"{lang_in}|{lang_out}"
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            result_text = response.json()["responseData"]["translatedText"]
            return [result_text[i:i+1000] for i in range(0, len(result_text), 1000)]
        else:
            print(f"MyMemory API xatosi: {response.status_code}")
            return None
    except Exception as e:
        print(f"MyMemory API xatosi: {e}")
        return None

# Asosiy tarjima funksiyasi
async def text_translate(text, user_id):
    # Foydalanuvchi tilini bazadan olish
    sql.execute(f"""SELECT in_lang FROM public.user_langs WHERE user_id={user_id}""")
    lang_in = sql.fetchone()[0]

    sql.execute(f"""SELECT out_lang FROM public.user_langs WHERE user_id={user_id}""")
    lang_out = sql.fetchone()[0]

    # Tarjima usullarini ro'yxatga joylash
    translation_methods = [
        translate_with_deep_translator,
        translate_with_googletrans,
        translate_with_mymemory
    ]

    # Random tarzda tarjima usulini tanlash
    import random
    selected_method = random.choice(translation_methods)

    # Tanlangan usul yordamida tarjima qilish
    result_text = selected_method(text, lang_in, lang_out)

    # Agar tanlangan usul ishlamasa, boshqa usullarni sinab ko'rish
    if result_text is None:
        for method in translation_methods:
            if method != selected_method:
                result_text = method(text, lang_in, lang_out)
                if result_text is not None:
                    break

    # Agar hech qanday usul ishlamasa, xabar qaytarish
    if result_text is None:
        result_text = ["Tarjima qilishda xatolik yuz berdi."]

    return lang_out, result_text


# async def text_translate(text, user_id):
#     sql.execute(f"""SELECT in_lang FROM public.user_langs WHERE user_id={user_id}""")
#     lang_in = sql.fetchone()[0]
#
#     sql.execute(f"""SELECT out_lang FROM public.user_langs WHERE user_id={user_id}""")
#     lang_out = sql.fetchone()[0]
#     try:
#         from deep_translator import GoogleTranslator
#         tr = GoogleTranslator(source=lang_in, target=lang_out)
#         result_text = str(tr.translate(text=text))
#         result_text = [result_text[i:i+1000] for i in range(0, len(result_text), 1000)]
#     except:
#         try:
#             from googletrans import Translator
#             translator = Translator()
#             translation = translator.translate("Salom", src=lang_in, dest=lang_out)
#             result_text = translation.text
#             result_text = [result_text[i:i + 1000] for i in range(0, len(result_text), 1000)]
#         except:
#             try:
#                 url = "https://api.mymemory.translated.net/get"
#                 params = {
#                     "q": text,
#                     "langpair": f"{lang_in}|{lang_out}"
#                 }
#                 response = requests.get(url, params=params)
#                 if response.status_code == 200:
#                     result_text = response.json()["responseData"]["translatedText"]
#                     result_text = [result_text[i:i + 1000] for i in range(0, len(result_text), 1000)]
#                 else:
#                     result_text = "ERROR"
#             except:
#                 result_text = "ERROR"
#
#     return lang_out, result_text

@router.message(Command("lang"), F.chat.type == "private")
async def change_lang(message: Message, bot: Bot):
    user_id = message.from_user.id
    await bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
    await Authenticator.auth_user(message)
    await message.answer("Choose languages", reply_markup=await UserPanels.langs_inline(user_id))

@router.message(F.content_type == ContentType.TEXT, F.chat.type == "private")
async def translator(message: Message, bot: Bot):
    exchangeLang = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Exchange Languages", callback_data="exchangeLang")],
        [InlineKeyboardButton(text="👅 Langs", callback_data="lang_list")]
    ])

    await bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)
    await Authenticator.auth_user(message)
    user_id = message.from_user.id

    try:
        if await CheckData.check_member(bot, message.from_user.id) or user_id in adminPanel:
            lang_out, res_text = await text_translate(text=message.text, user_id=user_id)
            sql.execute(f"""SELECT tts FROM public.users_tts WHERE user_id={user_id}""")
            tts = sql.fetchone()[0]
            if tts and lang_out in ["en", "it", "ru", "korean", "ar", "zh-CN", "fr", "de", "hi", "id", "fa", "bn"]:
                for res in res_text:
                    try:
                        audio_path = f"{BASE_DIR}Audios/{user_id}.mp3"
                        tts = gTTS(text=str(res_text), lang=str(lang_out))
                        tts.save(str(audio_path))

                        await message.answer_audio(audio=FSInputFile(audio_path),
                                                   caption=f"<code>{res}</code>", parse_mode="html",
                                                   reply_markup=exchangeLang)
                    except Exception as e:
                        print(e)
                        await message.answer(text=f"<code>{res}</code>", parse_mode="html",
                                             reply_markup=exchangeLang)
            else:
                for res in res_text:
                    await message.answer(text=f"<code>{res}</code>", parse_mode="html", reply_markup=exchangeLang)

        else:
            await message.answer(
                "Botimizdan foydalanish uchun kanalimizga azo bo'ling\nSubscribe to our channel to use our bot",
                reply_markup=await UserPanels.join_btn(user_id))
    except Exception as ex:
        await bot.forward_message(chat_id=adminStart, from_chat_id=message.chat.id, message_id=message.message_id)
        await bot.send_message(chat_id=adminStart, text=f"Error in translation: \n\n{ex}\n\n\n{message.from_user}")


@router.message(F.content_type.in_([ContentType.VOICE, ContentType.AUDIO]), F.chat.type == "private")
async def show_lang_list(message: Message, bot: Bot):
    import asyncio
    asyncio.create_task(audio_tr(message, bot))  # Asinxron vazifani fon jarayoniga o'tkazish

async def audio_tr(message: Message, bot: Bot):
    user_id = message.from_user.id
    sent_msg = await bot.send_message(
        chat_id=user_id,
        text="Bu jarayon ko'proq vaqt olishi mumkin, kuting...\nWaiting a few seconds..."
    )

    if message.voice:
        file_id = message.voice.file_id
        file_format = "voice"
        file_name = message.voice.file_unique_id
    elif message.audio:
        file_id = message.audio.file_id
        file_format = "audio"
        file_name = message.audio.file_unique_id

    file_info = await bot.get_file(file_id)
    file_path = file_info.file_path
    downloaded_file = await bot.download_file(file_path)
    temp_file_path = rf"{BASE_DIR}audio_tr/{file_name}.{file_format}"

    with open(temp_file_path, "wb") as new_file:
        new_file.write(downloaded_file.read())

    if file_format == "voice":
        audio = AudioSegment.from_ogg(temp_file_path)
    else:
        audio = AudioSegment.from_file(temp_file_path)

    audio_name = rf"{BASE_DIR}audio_tr/{file_name}.wav"
    audio.export(audio_name, format="wav")
    os.remove(temp_file_path)

    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_name) as source:
        audio1 = recognizer.record(source)

    sql.execute(f"""SELECT in_lang FROM public.user_langs WHERE user_id={user_id}""")
    lang_in = sql.fetchone()[0]
    exchangeLang = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Exchange Languages", callback_data="exchangeLang")],
        [InlineKeyboardButton(text="👅 Langs", callback_data="lang_list")]
    ])

    try:
        language_map = {
        "uz": "uz-UZ",
        "tr": "tr-TR",
        "tg": "tg-TJ",
        "en": "en-US",
        "ja": "ja-JP",
        "it": "it-IT",
        "ru": "ru-RU",
        "korean": "ko-KR",
        "ar": "ar-SA",
        "zh-CN": "zh-CN",
        "fr": "fr-FR",
        "de": "de-DE",
        "hi": "hi-IN",
        "az": "az-AZ",
        "af": "af-ZA",
        "kk": "kk-KZ",
        "tk": "tk-TM",
        "ky": "ky-KG",
        "am": "am-ET",
        "id": "id-ID",
        "fa": "fa-IR",
        "ug": "ug-CN",
        "ur": "ur-PK",
        "bn": "bn-BD",
        }
        text = recognizer.recognize_google(audio1, language=language_map[lang_in])
        lang_in, lang_out, res_text, ikkili, off, simple = await text_translate(text=text, user_id=user_id)
        if ikkili or simple:
            for i in res_text:
                await bot.send_message(chat_id=user_id, text=i, parse_mode="html", reply_markup=exchangeLang)
        elif off:
            res_text = res_text[0]
            await bot.send_message(chat_id=user_id, text=res_text, parse_mode="html", reply_markup=exchangeLang)
        else:
            await bot.send_message(chat_id=user_id, text=f"<code>{res_text}</code>", parse_mode="html", reply_markup=exchangeLang)

        await bot.delete_message(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id)
    except Exception as ex:
        await bot.send_message(chat_id=user_id, text="Audio tushunarsiz!\n\nThe audio is unclear")
        await bot.delete_message(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id)
        await bot.forward_message(chat_id=adminStart, from_chat_id=message.chat.id, message_id=message.message_id)
        await bot.send_message(chat_id=adminStart, text=f"Error text: \n\n<code>{ex}</code>\n\n\n{message.chat}",
                               parse_mode="html")
