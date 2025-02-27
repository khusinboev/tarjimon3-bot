from aiogram import types
import asyncio
from config import db, sql, conSql, curSql


async def create_all_base():
    sql.execute("""CREATE TABLE IF NOT EXISTS public.accounts
(
    id SERIAL NOT NULL,
    user_id bigint NOT NULL,
    username character varying(32),
    lang_code character varying(10),
    CONSTRAINT accounts_pkey PRIMARY KEY (id)
)""")
    db.commit()

    sql.execute("""CREATE TABLE IF NOT EXISTS public.channels
(
    id SERIAL NOT NULL,
    chat_id bigint NOT NULL,
    title character varying,
    username character varying,
    types character varying,
    CONSTRAINT channels_pkey PRIMARY KEY (id)
)""")
    db.commit()

    sql.execute("""CREATE TABLE IF NOT EXISTS public.groups
(
    id SERIAL NOT NULL,
    chat_id bigint NOT NULL,
    title character varying,
    username character varying,
    types character varying,
    CONSTRAINT groups_pkey PRIMARY KEY (id)
)""")
    db.commit()

    sql.execute("""CREATE TABLE IF NOT EXISTS public.group_langs
(
    chat_id bigint NOT NULL,
    in_lang character varying(25) NOT NULL DEFAULT 'uz',
    out_lang character varying NOT NULL DEFAULT 'en',
    CONSTRAINT group_langs_pkey PRIMARY KEY (chat_id)
)""")
    db.commit()

    sql.execute("""CREATE TABLE IF NOT EXISTS public.mandatorys
(
    id SERIAL NOT NULL,
    chat_id character varying NOT NULL,
    CONSTRAINT mandatorys_pkey PRIMARY KEY (id)
)""")
    db.commit()

    sql.execute("""CREATE TABLE IF NOT EXISTS public.user_langs
(
    user_id bigint NOT NULL,
    in_lang character varying(25) NOT NULL DEFAULT 'uz',
    out_lang character varying(25) NOT NULL DEFAULT 'en',
    langs TEXT NOT NULL DEFAULT 'all',
    CONSTRAINT user_langs_pkey PRIMARY KEY (user_id)
)""")
    db.commit()

    sql.execute("""CREATE TABLE IF NOT EXISTS public.users_status
(
    user_id bigint NOT NULL,
    date date NOT NULL,
    active_date date,
    CONSTRAINT users_status_pkey PRIMARY KEY (user_id)
)""")
    db.commit()

    sql.execute("""CREATE TABLE IF NOT EXISTS public.users_tts
(
    user_id bigint NOT NULL,
    tts boolean NOT NULL DEFAULT false,
    CONSTRAINT users_tts_pkey PRIMARY KEY (user_id)
)""")
    db.commit()

    sql.execute("""
CREATE OR REPLACE FUNCTION public.user_lang()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE NOT LEAKPROOF
AS $BODY$
begin
	insert into user_langs( user_id, in_lang, out_lang )
	values( new.user_id, 'uz', 'en' );
	return null;
end
$BODY$;
ALTER FUNCTION public.user_lang()
    OWNER TO postgres;""")
    db.commit()

    sql.execute("""CREATE OR REPLACE FUNCTION public.user_status()
                        RETURNS trigger
                        LANGUAGE 'plpgsql'
                        COST 100
                        VOLATILE NOT LEAKPROOF
                    AS $BODY$
                    begin
                        insert into users_status( user_id, date, active_date )
                        values( new.user_id, date( current_date at time zone 'Asia/Tashkent' ), date( current_date at time zone 'Asia/Tashkent' ) );
                        return null;
                    end
                    $BODY$;
                    ALTER FUNCTION public.user_status()
                        OWNER TO postgres;""")
    db.commit()

    sql.execute("""
CREATE OR REPLACE FUNCTION public.user_tts()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE NOT LEAKPROOF
AS $BODY$
begin
	insert into users_tts( user_id, tts )
	values( new.user_id, 'false' );
	return Null;
end
$BODY$;

ALTER FUNCTION public.user_tts()
    OWNER TO postgres;""")
    db.commit()

    sql.execute("""CREATE OR REPLACE FUNCTION public.group_lang()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE NOT LEAKPROOF
AS $BODY$
begin
	insert into group_langs( chat_id, in_lang, out_lang )
	values( new.chat_id, 'uz', 'en' );
	return null;
end
$BODY$;

ALTER FUNCTION public.group_lang()
    OWNER TO postgres;
""")
    db.commit()

    sql.execute("""CREATE OR REPLACE TRIGGER group_lang
    AFTER INSERT
    ON public.groups
    FOR EACH ROW
    EXECUTE FUNCTION public.group_lang();""")
    db.commit()

    sql.execute("""CREATE OR REPLACE TRIGGER user_lang
    AFTER INSERT
    ON public.accounts
    FOR EACH ROW
    EXECUTE FUNCTION public.user_lang();""")
    db.commit()

    sql.execute("""CREATE OR REPLACE TRIGGER user_status
    AFTER INSERT
    ON public.accounts
    FOR EACH ROW
    EXECUTE FUNCTION public.user_status();""")
    db.commit()

    sql.execute("""CREATE OR REPLACE TRIGGER user_tts
    AFTER INSERT
    ON public.accounts
    REFERENCING NEW TABLE AS new
    FOR EACH ROW
    EXECUTE FUNCTION public.user_tts();""")
    db.commit()

    sql.execute("""CREATE TABLE IF NOT EXISTS public.langs_list
(
    lang_in character varying(15) NOT NULL,
    lang_out character varying(15) NOT NULL,
    code character varying(10) NOT NULL,
    status boolean NOT NULL DEFAULT true,
    CONSTRAINT langs_list_pkey PRIMARY KEY (lang_in, lang_out, code)
)""")
    db.commit()

    sql.execute("""select code from public.langs_list""")
    check = sql.fetchone()
    if check is None:

        langL1 = ["🇺🇿O`zbek", "🇹🇷Turk", "🇹🇯Tajik", "🇬🇧English", "🇯🇵Japan", "🇮🇹Italian", "🇷🇺Русский", "🇰🇷Korean",
                  "🇸🇦Arabic", "🇨🇳Chinese", "🇫🇷French", "🇩🇪German", "🇮🇳Hindi", "🇦🇿Azerbaijan", "🇦🇫Afghan", "🇰🇿Kazakh",
                  "🇹🇲Turkmen", "🇰🇬Kyrgyz", "🇪🇹Ethiopia", "🇮🇩Indonesian"]

        langL2 = ["🇺🇿 O`zbek", "🇹🇷 Turk", "🇹🇯 Tajik", "🇬🇧 English", "🇯🇵 Japan", "🇮🇹 Italian", "🇷🇺 Русский", "🇰🇷 Korean",
                  "🇸🇦 Arabic", "🇨🇳 Chinese", "🇫🇷 French", "🇩🇪 German", "🇮🇳 Hindi", "🇦🇿 Azerbaijan", "🇦🇫 Afghan", "🇰🇿 Kazakh",
                  "🇹🇲 Turkmen", "🇰🇬 Kyrgyz", "🇪🇹 Ethiopia", "🇮🇩 Indonesian"]

        codes = ["uz", "tr", "tg", "en", "ja", "it", "ru", "korean", "ar", "zh-CN", "fr", "de", "hi", "az", "af", "kk",
                 "tk", "ky", "am", "id"]
        for lang1, lang2, code in zip(langL1, langL2, codes):
            sql.execute(f"""INSERT INTO public.langs_list (lang_in, lang_out, code) VALUES ('{lang1}', '{lang2}', '{code}');""")
            db.commit()


class Authenticator:
    @staticmethod
    async def auth_user(message: types.Message):
        try:
            user_id = message.from_user.id
            username = message.from_user.username
            lang_code = message.from_user.language_code

            sql.execute(f"""SELECT user_id FROM accounts WHERE user_id = {user_id}""")
            check = sql.fetchone()
            if check is None:
                sql.execute(f"DELETE FROM public.accounts WHERE user_id ='{user_id}'")
                db.commit()
                sql.execute(f"DELETE FROM public.user_langs WHERE user_id ='{user_id}'")
                db.commit()
                sql.execute(f"DELETE FROM public.users_status WHERE user_id ='{user_id}'")
                db.commit()
                sql.execute(f"DELETE FROM public.users_tts WHERE user_id ='{user_id}'")
                db.commit()
                # sana = datetime.datetime.now(pytz.timezone('Asia/Tashkent')).strftime('%d-%m-%Y %H:%M')
                sql.execute(f"INSERT INTO accounts (user_id, username, lang_code) "
                            f"VALUES ('{user_id}', '{username}', '{lang_code}')")
                db.commit()
        except: pass

    @staticmethod
    async def auth_group(message: types.Message):
        chat_id = message.chat.id
        group_type = message.chat.type
        sql.execute(f"""SELECT chat_id FROM groups WHERE chat_id = {chat_id}""")
        check = sql.fetchone()
        if check is None:
            sql.execute(f"""INSERT INTO groups (chat_id, types) VALUES ('{chat_id}', '{group_type}')""")
            db.commit()


class DefinitionEn:
    @staticmethod
    async def defination_en(text):
        curSql.execute("SELECT Word, Type, Description FROM definition WHERE Word = ? COLLATE NOCASE", (text,))
        results = curSql.fetchall()
        resultsList = []
        # Natija mavjudligini tekshirish
        if results:
            res_text = ''
            num = 0
            for row in results:
                word, word_type, word_description = row
                res_text += f"<b>{word}</b><i>{'' if word_type == '()' else word_type}</i> - <code>{word_description}</code>\n\n"
                num += 1
            pr=len(res_text) // 4096
            if pr == 0:
                resultsList.append(res_text)
            else:
                res_text2 = ''
                num2 = 0
                for row in results:
                    word, word_type, word_description = row
                    res_text2 += f"<b>{word}</b><i>{'' if word_type == '()' else word_type}</i> - <code>{word_description}</code>\n\n"
                    num2 += 1
                    if num2 % (num//(pr+1)) == 0:
                        resultsList.append(res_text2)
                        res_text2 = ''
        else: resultsList = [None]
        return resultsList

    @staticmethod
    async def uzb_eng(text):
        resultsList = []

        curSql.execute("""SELECT "uzb", "eng" FROM "uzb_eng" WHERE "uzb" = ? COLLATE NOCASE""", (text,))
        results = curSql.fetchall()

        if not results:
            curSql.execute("""SELECT "uzb", "eng" FROM "uzb_eng" WHERE "uzb" LIKE ? COLLATE NOCASE""", (text + '%',))
            results = curSql.fetchall()

        if not results:
            curSql.execute("""SELECT "uzb", "eng" FROM "uzb_eng" WHERE "uzb" LIKE ? COLLATE NOCASE""",
                           ('%' + text + '%',))
            results = curSql.fetchall()

        if results:
            res_text = ''
            for row in results:
                uzb, eng = row
                res_text += f"<b>{uzb}</b> - {eng}\n"

            pr = len(res_text) // 4096
            if pr == 0:
                resultsList.append(res_text)
            else:
                res_text2 = ''
                for i, row in enumerate(results):
                    uzb, eng = row
                    res_text2 += f"<b>{uzb}</b> - {eng}\n"
                    if (i + 1) % (len(results) // (pr + 1)) == 0:
                        resultsList.append(res_text2)
                        res_text2 = ''

                if res_text2:
                    resultsList.append(res_text2)
        else:
            resultsList.append(None)

        return resultsList

    @staticmethod
    async def eng_uzb(text):
        resultsList = []

        # 1-qadam: Ayni o'zini izlash
        curSql.execute("""SELECT "eng", "pron", "uzb" FROM "eng_uzb" 
                              WHERE "eng" = ? COLLATE NOCASE""", (text,))
        results = curSql.fetchall()

        # 2-qadam: Agar aniq natija topilmasa, boshlanishiga qarab izlash
        if not results:
            curSql.execute("""SELECT "eng", "pron", "uzb" FROM "eng_uzb" 
                                  WHERE "eng" LIKE ? COLLATE NOCASE""", (text + '%',))
            results = curSql.fetchall()

        # 3-qadam: Agar boshlanishi ham topilmasa, ichida mavjudligini izlash
        if not results:
            curSql.execute("""SELECT "eng", "pron", "uzb" FROM "eng_uzb" 
                                  WHERE "eng" LIKE ? COLLATE NOCASE""", ('%' + text + '%',))
            results = curSql.fetchall()

        # 4-qadam: Natijalarni qayta ishlash
        if results:
            res_text = ''
            for row in results:
                eng, pron, uzb = row
                res_text += f"<b>{eng}</b> <i>{pron}</i> - {uzb}\n\n"

            # 5-qadam: 4096 dan katta bo'lsa bo'lib yuborish
            pr = len(res_text) // 4096
            if pr == 0:
                resultsList.append(res_text)
            else:
                res_text2 = ''
                for i, row in enumerate(results):
                    eng, pron, uzb = row
                    res_text2 += f"<b>{eng}</b> <i>{pron}</i> - {uzb}\n\n"
                    # Har bir bo'lakka teng taqsimlash
                    if (i + 1) % (len(results) // (pr + 1)) == 0:
                        resultsList.append(res_text2)
                        res_text2 = ''

                # Oxirgi bo'lakni ham qo'shish
                if res_text2:
                    resultsList.append(res_text2)
        else:
            resultsList.append(None)
        return resultsList
