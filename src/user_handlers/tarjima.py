from aiogram import Router, Bot, F
from aiogram.enums import ChatAction
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ContentType
from aiogram.filters import Command
from aiogram.utils.chat_action import ChatActionSender
from deep_translator import GoogleTranslator
from pydub import AudioSegment
from gtts import gTTS
import speech_recognition as sr
import os

from src.buttons.buttons import UserPanels
from src.config import sql, adminPanel, adminStart
from src.database.functions import Authenticator
from src.functions.functions import CheckData

router = Router()


async def text_translate(text, user_id):
    sql.execute(f"""SELECT in_lang FROM public.user_langs WHERE user_id={user_id}""")
    lang_in = sql.fetchone()[0]

    sql.execute(f"""SELECT out_lang FROM public.user_langs WHERE user_id={user_id}""")
    lang_out = sql.fetchone()[0]

    translator = GoogleTranslator(source=lang_in, target=lang_out)
    trText = str(translator.translate(text))
    return lang_in, lang_out, trText

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
        if await CheckData.check_on_start(message.chat.id) or user_id in adminPanel:
            lang_in, lang_out, trText = await text_translate(text=message.text, user_id=user_id)

            sql.execute(f"""SELECT tts FROM public.users_tts WHERE user_id={user_id}""")
            tts = sql.fetchone()[0]

            if trText is None:
                await message.answer(text=message.text, reply_markup=exchangeLang)
            elif len(trText) < 4096:
                if tts:
                    try:
                        audio_path = f"Audios/{user_id}.mp3"
                        tts = gTTS(text=trText, lang=lang_out)
                        tts.save(audio_path)

                        await message.answer_audio(audio=audio_path, caption=f"<code>{trText}</code>",
                                                   parse_mode="html", reply_markup=exchangeLang)
                    except:
                        await message.answer(text=f"<code>{trText}</code>", parse_mode="html", reply_markup=exchangeLang)
                else:
                    await message.answer(text=f"<code>{trText}</code>", parse_mode="html", reply_markup=exchangeLang)
            else:
                num = trText.split()
                fT = " ".join(num[:(len(num) // 2)])
                tT = " ".join(num[(len(num) // 2):])
                try:
                    audio_path = f"Audios/{user_id}.mp3"
                    tts = gTTS(text=trText, lang=lang_out)
                    tts.save(audio_path)

                    await message.answer_audio(audio_path, caption=f"<code>{fT}</code>",
                                               parse_mode="html", reply_markup=exchangeLang)
                    await message.answer(text=f"<code>{tT}</code>", parse_mode="html", reply_markup=exchangeLang)
                except:
                    await message.answer(text=f"<code>{fT}</code>", parse_mode="html", reply_markup=exchangeLang)
                    await message.answer(text=f"<code>{tT}</code>", parse_mode="html", reply_markup=exchangeLang)
        else:
            await message.answer(
                "Botimizdan foydalanish uchun kanalimizga azo bo'ling\nSubscribe to our channel to use our bot",
                reply_markup=await UserPanels.join_btn(user_id))
    except Exception as ex:
        await bot.forward_message(chat_id=adminStart, from_chat_id=message.chat.id, message_id=message.message_id)
        await bot.send_message(chat_id=adminStart, text=f"Error in translation: \n\n{ex}\n\n\n{message.from_user}")


@router.message(F.content_type.in_([ContentType.VOICE, ContentType.AUDIO]), F.chat.type == "private")
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
    temp_file_path = f"{file_name}.{file_format}"

    with open(temp_file_path, "wb") as new_file:
        new_file.write(downloaded_file.read())

    if file_format == "voice":
        audio = AudioSegment.from_ogg(temp_file_path)
    else:
        audio = AudioSegment.from_file(temp_file_path)

    audio_name = f"audio_tr/{file_name}.wav"
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
        text = recognizer.recognize_google(audio1, language=lang_in)
        lang_in, lang_out, trText = await text_translate(text=text, user_id=user_id)
        await bot.send_message(chat_id=user_id, text=f"<code>{trText}</code>", parse_mode="html",
                               reply_markup=exchangeLang)
        await bot.delete_message(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id)
    except Exception as ex:
        await bot.send_message(chat_id=user_id, text="Audio tushunarsiz!\n\nThe audio is unclear")
        await bot.delete_message(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id)
        await bot.forward_message(chat_id=adminStart, from_chat_id=message.chat.id, message_id=message.message_id)
        await bot.send_message(chat_id=adminStart, text=f"Error text: \n\n<code>{ex}</code>\n\n\n{message.chat}",
                               parse_mode="html")
