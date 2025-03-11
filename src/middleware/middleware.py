import psycopg2
from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery, ChatMemberUpdated
from typing import Callable, Dict, Any, Awaitable
import pytz
from datetime import datetime

from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

# PostgreSQL ulanish parametrlari
DB_CONFIG = {
    "dbname": DB_NAME,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "host": DB_HOST,
    "port": DB_PORT
}


class AuthMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.init_db()  # Bot ishga tushganda jadvallarni yaratish

    def init_db(self):
        """Jadvallarni yaratish (agar bo'lmasa)"""
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                lang_code TEXT
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS users_status (
                user_id BIGINT PRIMARY KEY,
                date DATE,
                active_date DATE
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                chat_id BIGINT PRIMARY KEY,
                types TEXT
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS users_tts (
                user_id BIGINT PRIMARY KEY,
                setting TEXT DEFAULT 'default'
            );
        """)

        conn.commit()
        cur.close()
        conn.close()

    async def __call__(
            self, handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update, data: Dict[str, Any]
    ) -> Any:
        """Har bir yangilanish kelganda foydalanuvchi yoki guruhni bazaga qo‘shish"""

        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        user_id = None
        username = None
        lang_code = None
        chat_id = None
        chat_type = None

        if event.message:  # Agar xabar bo‘lsa
            user = event.message.from_user
            chat = event.message.chat
        elif event.callback_query:  # Agar callback tugma bo‘lsa
            user = event.callback_query.from_user
            chat = event.callback_query.message.chat
        elif event.chat_member:  # Agar guruhga qo‘shilgan bo‘lsa
            user = event.chat_member.new_chat_member.user
            chat = event.chat_member.chat
        else:
            return await handler(event, data)

        user_id = user.id
        username = user.username or "NoUsername"
        lang_code = user.language_code or "uz"
        chat_id = chat.id
        chat_type = chat.type

        # Foydalanuvchini tekshirish va qo‘shish
        cur.execute("SELECT user_id FROM accounts WHERE user_id = %s", (user_id,))
        user_check = cur.fetchone()

        if not user_check:
            now_tashkent = datetime.now(pytz.timezone('Asia/Tashkent')).date()

            cur.execute("DELETE FROM accounts WHERE user_id = %s", (user_id,))
            cur.execute("DELETE FROM users_status WHERE user_id = %s", (user_id,))
            cur.execute("DELETE FROM users_tts WHERE user_id = %s", (user_id,))

            cur.execute(
                "INSERT INTO accounts (user_id, username, lang_code) VALUES (%s, %s, %s)",
                (user_id, username, lang_code)
            )
            cur.execute(
                "INSERT INTO users_status (user_id, date, active_date) VALUES (%s, %s, %s)",
                (user_id, now_tashkent, now_tashkent)
            )

        # Guruh yoki kanalni tekshirish va qo‘shish
        if chat_type in ["supergroup", "group", "channel"]:
            cur.execute("SELECT chat_id FROM groups WHERE chat_id = %s", (chat_id,))
            group_check = cur.fetchone()

            if not group_check:
                cur.execute(
                    "INSERT INTO groups (chat_id, types) VALUES (%s, %s)",
                    (chat_id, chat_type)
                )

        conn.commit()
        cur.close()
        conn.close()

        return await handler(event, data)
