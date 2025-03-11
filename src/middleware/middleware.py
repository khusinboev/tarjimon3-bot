from aiogram.types import Update
from aiogram.dispatcher.middlewares.base import BaseMiddleware
import psycopg2
from datetime import datetime
import pytz
from config import DB_CONFIG

class RegisterUserMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        if not event.message:
            return await handler(event, data)  # Middleware davom etsin

        user = event.message.from_user
        user_id = user.id
        username = user.username if user.username else None
        date = datetime.now(pytz.timezone("Asia/Tashkent")).date()
        lang_code = user.language_code if user.language_code else "uz"

        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # **1️⃣ SQL Injection xavfsizligi uchun f-string emas, parametr ishlatilmoqda**
        cur.execute("SELECT user_id FROM public.accounts WHERE user_id = %s", (user_id,))
        if not cur.fetchone():  # Foydalanuvchi bazada bo‘lmasa
            cur.execute("DELETE FROM public.accounts WHERE user_id = %s", (user_id,))
            cur.execute("DELETE FROM public.user_langs WHERE user_id = %s", (user_id,))
            cur.execute("DELETE FROM public.users_status WHERE user_id = %s", (user_id,))
            cur.execute("DELETE FROM public.users_tts WHERE user_id = %s", (user_id,))
            conn.commit()

            cur.execute(
                "INSERT INTO accounts (user_id, username, lang_code) VALUES (%s, %s, %s)",
                (user_id, username, lang_code)
            )
            conn.commit()

        cur.close()
        conn.close()

        return await handler(event, data)  # **2️⃣ Xatolik tuzatildi, middleware davom etadi**
