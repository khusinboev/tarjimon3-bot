from aiogram.types import CallbackQuery

from src.config import sql, db


class Lang:
    @staticmethod
    async def user_lang_update(call: CallbackQuery):
        print("tillarni yangilash bo'limi")
        data = (call.data)[1:]
        user_id = call.from_user.id
        sql.execute(f"""select langs from public.user_langs where user_id={user_id}""")
        vaj = sql.fetchone()[0]
        if  vaj:
            langs_read = [langs for langs in vaj.split(", ") if langs]
            if call.data in await Lang.lang_list():
                if langs_read[0] == "all":
                    sql.execute(f"""UPDATE public.user_langs SET langs = '{data}' WHERE user_id='{user_id}'""")
                    db.commit()
                elif data in langs_read:
                    langs_read.remove(data)
                    sql.execute(f"""UPDATE public.user_langs SET langs = '{", ".join(langs_read)}' WHERE user_id='{user_id}'""")
                    db.commit()
                else:
                    langs_read.append(data)
                    sql.execute(f"""UPDATE public.user_langs SET langs = '{", ".join(langs_read)}' WHERE user_id='{user_id}'""")
                    db.commit()
        else:
            sql.execute(f"""UPDATE public.user_langs SET langs = '{data}' WHERE user_id='{user_id}'""")
            db.commit()

    @staticmethod
    async def user_lang_check(call: CallbackQuery):
        user_id = call.from_user.id
        if ' ' in call.data:
            sql.execute(f"""select code from public.langs_list where lang_out='{call.data}'""")
            code = sql.fetchone()[0]

            sql.execute(f"""UPDATE public.user_langs SET out_lang = '{code}' WHERE user_id='{user_id}'""")
            db.commit()
        elif call.data == 'TTS':
            sql.execute(f"""select tts from public.users_tts where user_id={user_id}""")
            tts = sql.fetchone()[0]
            sql.execute(f"""UPDATE public.users_tts SET tts = {not tts} WHERE user_id='{user_id}'""")
            db.commit()
        else:
            sql.execute(f"""select code from public.langs_list where lang_in='{call.data}'""")
            code = sql.fetchone()[0]
            sql.execute(f"""UPDATE public.user_langs SET in_lang = '{code}' WHERE user_id='{user_id}'""")
            db.commit()

    @staticmethod
    async def lang_list():
        sql.execute(f"""select code from public.langs_list""")
        code = ["_"+str(item[0]) for item in sql.fetchall()]
        return code

    @staticmethod
    async def user_langs(user_id):
        sql.execute(f"""select lang_in from public.langs_list where code=(select in_lang from public.user_langs where user_id={user_id})""")
        user_in = sql.fetchone()[0]

        sql.execute(f"""select lang_out from public.langs_list where code=(select out_lang from public.user_langs where user_id={user_id})""")
        user_out = sql.fetchone()[0]

        return user_in, user_out

    @staticmethod
    async def lang_list_users(user_id):
        sql.execute(f"""select langs from public.user_langs where user_id={user_id}""")
        langs_read = [langs for langs in sql.fetchone()[0].split(", ")]
        sql.execute(f"""select lang_in, code from public.langs_list""")
        lang_ins = sql.fetchall()
        sql.execute(f"""select lang_out, code from public.langs_list""")
        lang_outs = sql.fetchall()
        if "all"in langs_read: return [item[0] for item in lang_ins], [item[0] for item in lang_outs]
        else:
            return ([item[0] for item in lang_ins if item[1] in langs_read],
                    [item[0] for item in lang_outs if item[1] in langs_read])

    @staticmethod
    async def lang_list2():
        sql.execute(f"""select lang_in, code from public.langs_list""")
        lang_ins = sql.fetchall()
        return [item[0] for item in lang_ins], ["_"+str(item[1]) for item in lang_ins]