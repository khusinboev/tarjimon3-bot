from aiogram.types import Update
from aiogram.dispatcher.middlewares.base import BaseMiddleware
import psycopg2
from datetime import datetime
import pytz
from config import DB_CONFIG

class RegisterUserMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        if not event.message:
            return

        user = event.message.from_user
        user_id = user.id
        username = user.username if user.username else None
        date = datetime.now(pytz.timezone("Asia/Tashkent")).date()
        lang_code = user.language_code if user.language_code else "uz"
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Foydalanuvchini tekshirish (bazada yo‘q bo‘lsa, qo‘shish)
        cur.execute("SELECT id FROM users_status WHERE user_id = %s", (user_id,))
        if not cur.fetchone():  # Agar foydalanuvchi bazada bo'lmasa
            cur.execute(f"DELETE FROM public.accounts WHERE user_id ='{user_id}'")
            conn.commit()
            cur.execute(f"DELETE FROM public.user_langs WHERE user_id ='{user_id}'")
            conn.commit()
            cur.execute(f"DELETE FROM public.users_status WHERE user_id ='{user_id}'")
            conn.commit()
            cur.execute(f"DELETE FROM public.users_tts WHERE user_id ='{user_id}'")
            conn.commit()
            # sana = datetime.datetime.now(pytz.timezone('Asia/Tashkent')).strftime('%d-%m-%Y %H:%M')
            cur.execute(f"INSERT INTO accounts (user_id, username, lang_code) "
                        f"VALUES ('{user_id}', '{username}', '{lang_code}')")
            conn.commit()

        cur.close()
        conn.close()
