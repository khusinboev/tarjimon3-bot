from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, KeyboardButton, InlineKeyboardMarkup

from src.config import sql, dp
from .function import Lang


class AdminPanel:
    @staticmethod
    async def admin_menu():
        btn=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="📊Statistika"),
                            KeyboardButton(text="🔧Kanallar"),
                        ],
                        # [
                        #     KeyboardButton(text="📤Reklama"),
                        #     KeyboardButton(text="♻️ Tozalash"),
                        # ]
                    ],
                    resize_keyboard=True,
                )
        return btn

    @staticmethod
    async def admin_channel():
        admin_channel=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="➕Kanal qo'shish"),
                            KeyboardButton(text="❌Kanalni olib tashlash"),
                        ],
                        [
                            KeyboardButton(text="📋 Kanallar ro'yxati"),
                            KeyboardButton(text="🔙Orqaga qaytish"),
                        ]
                    ],
                    resize_keyboard=True,
                )
        return admin_channel

    @staticmethod
    async def admin_anons():
        admin_message=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="📨Oddit forward"),
                            KeyboardButton(text="📬Oddiy xabar"),
                        ],
                        [
                            KeyboardButton(text="🔙Orqaga qaytish"),
                        ]
                    ],
                    resize_keyboard=True,
                )
        return admin_message


class LanguageInline:
    @staticmethod
    async def join_btn(user_id):
        sql.execute("SELECT chat_id FROM public.mandatorys")
        rows = sql.fetchall()
        join_inline = []
        title = 1
        for row in rows:
            all_details = await dp.bot.get_chat(chat_id=row[0])
            url = all_details['invite_link']
            join_inline.append([InlineKeyboardButton(text=f"{title} - kanal", url=url)])
            title += 1
        join_inline.append([InlineKeyboardButton(text="✅Obuna bo'ldim", callback_data="check")])
        button = InlineKeyboardMarkup(inline_keyboard=join_inline)
        return button

    @staticmethod
    async def langs_inline(user_id):
        # Foydalanuvchi tanlagan tillarni olish
        user_in, user_out = await Lang.user_langs(user_id)

        # TTS holatini tekshirish
        sql.execute("SELECT tts FROM public.users_tts WHERE user_id = %s", (user_id,))
        tts = sql.fetchone()[0]

        # Barcha tillar roʻyxatini olish
        lang_ins, lang_outs = await Lang.lang_list()

        # Inline klaviaturalar yaratish
        langs_inline = []
        for lang_in, lang_out in zip(lang_ins, lang_outs):
            Nin = "✅" if user_in == lang_in else ""
            Nout = "✅" if user_out == lang_out else ""
            langs_inline.append([
                InlineKeyboardButton(text=f"{Nin}{lang_in}", callback_data=lang_in),
                InlineKeyboardButton(text=f"{Nout}{lang_out}", callback_data=lang_out)
            ])

        # TTS tugmasini qoʻshish
        tts_text = "✅TTS" if tts else "☑️TTS"
        langs_inline.append([InlineKeyboardButton(text=tts_text, callback_data="TTS")])

        # Inline klaviaturalarni qaytarish
        return InlineKeyboardMarkup(inline_keyboard=langs_inline)
