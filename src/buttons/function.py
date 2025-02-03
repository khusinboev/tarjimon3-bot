from src.config import sql


class Lang:
    @staticmethod
    async def lang_list():
        sql.execute(f"""select lang_in from public.langs_list""")
        lang_ins = sql.fetchall()
        lang_ins = [item[0] for item in lang_ins]

        sql.execute(f"""select lang_out from public.langs_list""")
        lang_outs = sql.fetchall()
        lang_outs = [item[0] for item in lang_outs]

        return lang_ins, lang_outs

    @staticmethod
    async def user_langs(user_id):
        sql.execute(f"""select lang_in from public.langs_list where code=(
        select in_lang from public.user_langs where user_id={user_id})""")
        user_in = sql.fetchone()[0]

        sql.execute(f"""select lang_out from public.langs_list where code=(
        select out_lang from public.user_langs where user_id={user_id})""")
        user_out = sql.fetchone()[0]

        return user_in, user_out

    @staticmethod
    async def group_lang(chat_id):
        sql.execute(f"""select lang_in from public.langs_list where code=(
        select in_lang from public.group_langs where chat_id={chat_id})""")
        chat_in = sql.fetchone()[0]

        sql.execute(f"""select lang_out from public.langs_list where code=(
        select out_lang from public.group_langs where chat_id={chat_id})""")
        chat_out = sql.fetchone()[0]

        return chat_in, chat_out