from datetime import datetime, timedelta

import psycopg2
import pytz
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ChatType
from aiogram.fsm.state import StatesGroup, State
from dateutil.relativedelta import relativedelta

from src.buttons.buttons import AdminPanel
from config import sql, adminPanel
from src.functions.functions import PanelFunc
from src.middleware.middleware import DB_CONFIG

router = Router()

class Form(StatesGroup):
    ch_add = State()
    ch_delete = State()

    anons_forward = State()
    anons_simple = State()

    clear_base = State()


# Admin panelga kirish
@router.message(Command("panel", "admin"), F.from_user.id.in_(adminPanel), F.chat.type == ChatType.PRIVATE)#,
async def panel_handler(message: Message) -> None:
    await message.answer("panel", reply_markup=await AdminPanel.admin_menu())


markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[KeyboardButton(text="🔙Orqaga qaytish")]])
@router.message(F.text == "🔙Orqaga qaytish", F.chat.type == ChatType.PRIVATE, F.from_user.id.in_(adminPanel))
async def backs(message: Message, state: FSMContext):
    await message.reply("Orqaga qaytildi", reply_markup=await AdminPanel.admin_menu())
    await state.clear()


# Statistika
@router.message(F.text == "📊Statistika", F.chat.type == ChatType.PRIVATE, F.from_user.id.in_(adminPanel))
async def new(message: Message):
    now = datetime.now(pytz.timezone("Asia/Tashkent")).date()

    # Oxirgi 3 oy: joriy oy va undan oldingi 2 ta oy
    current_month = now.replace(day=1)
    months = [current_month - relativedelta(months=i) for i in range(3)]

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Jami foydalanuvchilar
    cur.execute("SELECT COUNT(*) FROM users_status")
    all_users = cur.fetchone()[0]

    # Oxirgi 3 oydagi jami foydalanuvchilar
    cur.execute("SELECT COUNT(*) FROM users_status WHERE date >= %s", (months[-1],))
    last_3_months = cur.fetchone()[0]

    # Har bir oy bo‘yicha statistikalar
    month_counts = {}
    for month in months:
        cur.execute(
            "SELECT COUNT(*) FROM users_status WHERE date >= %s AND date < %s",
            (month, month + relativedelta(months=1))
        )
        month_counts[month.strftime("%B")] = cur.fetchone()[0] or 0  # Oy nomlari

    # Oxirgi 7 kun statistikasi
    last_7_days = {}
    for i in range(7):
        date_str = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        cur.execute("SELECT COUNT(*) FROM users_status WHERE date = %s", (date_str,))
        last_7_days[date_str] = cur.fetchone()[0] or 0

    cur.close()
    conn.close()

    # Xabarni tayyorlash
    stats_text = (
        f"📊 *Foydalanuvchi Statistikasi:*\n\n"
        f"🔹 *Jami foydalanuvchilar:* {all_users}\n\n"
        f"📅 *Oxirgi 3 oy:* (Jami {last_3_months} ta)\n"
    )
    for month, count in month_counts.items():
        stats_text += f" - {month}: {count} ta\n"

    stats_text += "\n📆 *Oxirgi 7 kun:* (Jami {})\n".format(sum(last_7_days.values()))
    for day, count in last_7_days.items():
        stats_text += f" - {day}: {count} ta\n"

    await message.answer(stats_text, parse_mode="Markdown")


# Kanallar bo'limi
@router.message(F.text == '🔧Kanallar', F.chat.type == ChatType.PRIVATE, F.from_user.id.in_(adminPanel))
async def new(msg: Message):
    await msg.answer("Tanlang", reply_markup=await AdminPanel.admin_channel())


@router.message(F.text == "🔙Orqaga qaytish", F.chat.type == ChatType.PRIVATE, F.from_user.id.in_(adminPanel), Form.ch_add or Form.ch_delete)
async def backs(message: Message, state: FSMContext):
    await message.reply("Orqaga qaytildi", reply_markup=await AdminPanel.admin_channel())
    await state.clear()


@router.message(F.text == "➕Kanal qo'shish", F.chat.type == ChatType.PRIVATE, F.from_user.id.in_(adminPanel))
async def channel_add(message: Message, state: FSMContext):
    await message.reply("Kanal qo'shish uchun kanalning userini yuboring.\nMisol uchun @coder_admin",
                        reply_markup=markup)
    await state.set_state(Form.ch_add)


@router.message(Form.ch_add, F.chat.type == ChatType.PRIVATE, F.from_user.id.in_(adminPanel))
async def channel_add1(message: Message, state: FSMContext):
    channel_id = message.text.upper()
    sql.execute(f"SELECT chat_id FROM public.mandatorys WHERE chat_id = '{message.text.upper()}'")
    data = sql.fetchone()
    if data is None:
        if message.text[0] == '@':
            await PanelFunc.channel_add(channel_id)
            await state.clear()
            await message.reply("Kanal qo'shildi🎉🎉", reply_markup=await AdminPanel.admin_channel())
        else:
            await message.reply("Kanal useri xato kiritildi\nIltimos userni @coder_admin ko'rinishida kiriting",
                                reply_markup=await AdminPanel.admin_channel())
    else:
        await message.reply("Bu kanal avvaldan bor", reply_markup=await AdminPanel.admin_channel())
    await state.clear()


@router.message(F.text == "❌Kanalni olib tashlash", F.chat.type == ChatType.PRIVATE, F.from_user.id.in_(adminPanel))
async def channel_delete(message: Message, state: FSMContext):
    await message.reply("O'chiriladigan kanalning userini yuboring.\nMisol uchun @coder_admin", reply_markup=markup)
    await state.set_state(Form.ch_delete)


@router.message(Form.ch_delete, F.chat.type == ChatType.PRIVATE, F.from_user.id.in_(adminPanel))
async def channel_delete2(message: Message, state: FSMContext):
    channel_id = message.text.upper()
    sql.execute(f"""SELECT chat_id FROM public.mandatorys WHERE chat_id = '{channel_id}'""")
    data = sql.fetchone()

    if data is None:
        await message.reply("Bunday kanal yo'q", reply_markup=await AdminPanel.admin_channel())
    else:
        if message.text[0] == '@':
            await PanelFunc.channel_delete(channel_id)
            await state.clear()
            await message.reply("Kanal muvaffaqiyatli o'chirildi", reply_markup=await AdminPanel.admin_channel())
        else:
            await message.reply("Kanal useri xato kiritildi\nIltimos userni @coder_admin ko'rinishida kiriting",
                                reply_markup=await AdminPanel.admin_channel())

    await state.clear()


@router.message(F.text == "📋 Kanallar ro'yxati", F.chat.type == ChatType.PRIVATE, F.from_user.id.in_(adminPanel))
async def channel_list(message: Message):
    if len(await PanelFunc.channel_list()) > 3:
        await message.reply(await PanelFunc.channel_list())
    else:
        await message.reply("Hozircha kanallar yo'q")
