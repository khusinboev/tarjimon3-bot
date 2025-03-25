from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, KeyboardButton, InlineKeyboardMarkup

from config import sql, dp, bot
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


class UserPanels:
    @staticmethod
    async def join_btn(user_id):
        sql.execute("SELECT chat_id FROM public.mandatorys")
        rows = sql.fetchall()
        join_inline = []
        title = 1
        for row in rows:
            all_details = await bot.get_chat(chat_id=row[0])
            url = all_details.invite_link
            if not url:
                url = await bot.export_chat_invite_link(row[0])
            join_inline.append([InlineKeyboardButton(text=f"{title} - kanal", url=url)])
            title += 1
        join_inline.append([InlineKeyboardButton(text="✅Obuna bo'ldim", callback_data="check")])
        button = InlineKeyboardMarkup(inline_keyboard=join_inline)
        return button

    @staticmethod
    async def main_manu():
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="✅Tillarni tanlash"), types.KeyboardButton(text="⚙️Tillarni sozlash")],
                #[types.KeyboardButton(text="📑Yo'riqnoma"), types.KeyboardButton(text="️‼️Fikr bildirish")]
            ],
            resize_keyboard=True
        )

        return keyboard

    @staticmethod
    async def back_menu():
        back_btn = [[types.KeyboardButton(text="So'rovni tugatish")]]
        back_btn = types.ReplyKeyboardMarkup(keyboard=back_btn, resize_keyboard=True)
        return back_btn

    @staticmethod
    async def langs_inline(user_id):
        # Foydalanuvchi tanlagan tillarni olish
        user_in, user_out = await Lang.user_langs(user_id)

        # TTS holatini tekshirish
        sql.execute("SELECT tts FROM public.users_tts WHERE user_id = %s", (user_id,))
        tts = sql.fetchone()[0]

        # Barcha tillar roʻyxatini olish
        lang_ins, lang_outs = await Lang.lang_list_users(user_id)

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


    @staticmethod
    async def user_langs_inline(user_id):
        sql.execute(f"""select langs from public.user_langs where user_id={user_id}""")
        langs_read = [langs for langs in sql.fetchone()[0].split(", ")]
        langs_read = ["_"+str(item) for item in langs_read]


        # Barcha tillar roʻyxatini olish
        langs, codes = await Lang.lang_list2()

        # Inline klaviaturalar yaratish
        langs_inline = []
        ll = []
        num = 0
        for langs, code in zip(langs, codes):
            num += 1
            Nin = "✅" if code in langs_read else ""
            ll.append(InlineKeyboardButton(text=f"{Nin}{langs}", callback_data=code))
            if num == 2:
                langs_inline.append(ll)
                num = 0
                ll = []
        # Inline klaviaturalarni qaytarish
        return InlineKeyboardMarkup(inline_keyboard=langs_inline)