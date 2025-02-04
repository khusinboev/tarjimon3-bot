from aiogram.types import CallbackQuery

from src.config import sql, db, dp, adminPanel, bot


class CheckData:
    @staticmethod
    async def check_on_start(user_id):
        sql.execute("SELECT chat_id FROM public.mandatorys")
        rows = sql.fetchall()
        error_code = 0
        for row in rows:
            r = await bot.get_chat_member(chat_id=row[0], user_id=user_id)
            if (str(r.status) in ['member', 'creator', 'admin']) or (user_id in adminPanel):
                pass
            else:
                error_code = 1
        if error_code == 0:
            return True
        else:
            return False


class PanelFunc:
    @staticmethod
    async def channel_add(chat_id):
        sql.execute(f"INSERT INTO public.mandatorys( chat_id ) VALUES('{chat_id}');")
        db.commit()

    @staticmethod
    async def channel_delete(id):
        sql.execute(f'''DELETE FROM public.mandatorys WHERE chat_id = '{id}' ''')
        db.commit()

    @staticmethod
    async def channel_list():
        sql.execute("SELECT chat_id from public.mandatorys")
        str = ''
        for row in sql.fetchall():
            chat_id = row[0]
            try:
                all_details = await bot.get_chat(chat_id=chat_id)
                title = all_details.title
                channel_id = all_details.id
                info = all_details.description
                str += f"------------------------------------------------\nKanal useri: > {chat_id}\nKamal nomi: > {title}\nKanal id si: > {channel_id}\nKanal haqida: > {info}\n"
            except Exception as e:
                str += f"Kanalni admin qiling\n\nError: {e}"
        return str
