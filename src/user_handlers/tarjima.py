import asyncio
from pathlib import Path

from aiogram import Router, Bot, F
from aiogram.enums import ChatAction
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ContentType, FSInputFile
from aiogram.filters import Command
from deep_translator import GoogleTranslator
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


async def text_translate(text, user_id):
    sql.execute(f"""SELECT in_lang FROM public.user_langs WHERE user_id={user_id}""")
    lang_in = sql.fetchone()[0]

    sql.execute(f"""SELECT out_lang FROM public.user_langs WHERE user_id={user_id}""")
    lang_out = sql.fetchone()[0]
    tarjimachin = text.strip()
    ikkili = False
    off = False
    simple = False
    if lang_in==lang_out=='en' and len(tarjimachin.split(" "))==1 and len(tarjimachin) != 1:
        definition = await DefinitionEn.defination_en(tarjimachin)
        if definition[0] is None:
            tr = GoogleTranslator(source=lang_in, target=lang_out)
            result_text = str(tr.translate(text))
        elif len(definition) == 1:
            result_text = definition[0]
        else:
            result_text = definition
            ikkili = True
    elif lang_in=='uz' and lang_out=='en' and len(tarjimachin.split(" "))==1 and len(tarjimachin) != 1:
        uz_en = await DefinitionEn.uzb_eng(tarjimachin)
        if uz_en[0] is None:
            tr = GoogleTranslator(source=lang_in, target=lang_out)
            result_text = str(tr.translate(text))
        elif len(uz_en) == 1:
            result_text = uz_en[0]
        else:
            result_text = uz_en
            ikkili = True
    elif lang_in=='en' and lang_out=='uz' and len(tarjimachin.split(" "))==1 and len(tarjimachin) != 1:
        en_uz = await DefinitionEn.eng_uzb(tarjimachin)
        if en_uz[0] is None:
            tr = GoogleTranslator(source=lang_in, target=lang_out)
            result_text = str(tr.translate(text))
        elif len(en_uz) == 1:
            result_text = en_uz[0]
        else:
            result_text = en_uz
            ikkili = True
    else:
        tr = GoogleTranslator(source=lang_in, target=lang_out)
        result_text = str(tr.translate(text))
        off = False
        simple = True
        result_text = [result_text[i:i+1000] for i in range(0, len(result_text), 1000)]
    return lang_in, lang_out, result_text, ikkili, off, simple

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
        print(BASE_DIR)
        if await CheckData.check_on_start(message.chat.id) or user_id in adminPanel:
            lang_in, lang_out, res_text, ikkili, off, simple = await text_translate(text=message.text, user_id=user_id)
            sql.execute(f"""SELECT tts FROM public.users_tts WHERE user_id={user_id}""")
            tts = sql.fetchone()[0]
            print("bera galdi")
            print(tts)
            if ikkili:
                print(ikkili)
                for i in res_text:
                    await message.answer(text=i, parse_mode="html", reply_markup=exchangeLang)
            elif off:
                print("beraquu1")
                if res_text is None:
                    await message.answer(text=message.text, reply_markup=exchangeLang)
                else:
                    print(tts)
                    if tts:
                        try:
                            audio_path = f"{BASE_DIR}Audios/{user_id}.mp3"
                            tts = gTTS(text=res_text, lang=lang_out)
                            tts.save(audio_path)

                            await message.answer_audio(audio=FSInputFile(audio_path),
                                                       caption=f"<code>{res_text}</code>", parse_mode="html",
                                                       reply_markup=exchangeLang)
                        except Exception as e:
                            await message.answer(text=f"<code>{res_text}</code>", parse_mode="html",
                                                 reply_markup=exchangeLang)
                    else:
                        await message.answer(text=f"<code>{res_text}</code>", parse_mode="html",
                                             reply_markup=exchangeLang)

            elif simple:
                for part in res_text:
                    if tts:
                        audio_path = rf"{BASE_DIR}Audios/{user_id}.mp3"
                        print(audio_path)
                        print(lang_out)
                        if isinstance(audio_path, list):
                            audio_path = audio_path[0]
                        tts = gTTS(text=part, lang=lang_out)
                        tts.save(audio_path)

                        await message.answer_audio(audio=FSInputFile(audio_path),
                                                   caption=f"<code>{part}</code>", parse_mode="html",
                                                   reply_markup=exchangeLang)
                    # await message.answer(part, reply_markup=exchangeLang)
                    await asyncio.sleep(0.1)
                # await message.answer(text=res_text, parse_mode="html", reply_markup=exchangeLang)

            else:
                print("beraquu3")
                await message.answer(text=res_text, parse_mode="html", reply_markup=exchangeLang)
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
