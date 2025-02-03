from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ChatType, ContentType
from aiogram.fsm.state import StatesGroup, State

from src.buttons.buttons import AdminPanel
from src.config import adminPanel, sql, bot, adminStart, dp
from src.functions.functions import PanelFunc

router = Router()

class Form(StatesGroup):
    ch_add = State()
    ch_delete = State()

    anons_forward = State()
    anons_simple = State()

    clear_base = State()


# Admin panelga kirish
@router.message(F.from_user.id == 7634626544, F.text == "/panel", F.chat.type == ChatType.PRIVATE)#,
async def panel_handler(message: Message) -> None:
    text = message.text
    await message.answer("panel", reply_markup=await AdminPanel.admin_menu())


markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[KeyboardButton(text="🔙Orqaga qaytish")]])
@router.message(F.text == "🔙Orqaga qaytish", F.chat.type == ChatType.PRIVATE, F.from_user.id == 7634626544)
async def backs(message: Message, state: FSMContext):
    await message.reply("Orqaga qaytildi", reply_markup=await AdminPanel.admin_menu())
    await state.clear()


# Statistika
@router.message(F.text == "📊Statistika", F.chat.type == ChatType.PRIVATE, F.from_user.id == 7634626544)
async def new(msg: Message):
    sql.execute("SELECT COUNT(*) FROM accounts")
    all_subscriber = sql.fetchone()[0]
    await msg.answer(
        f"👥Botdagi jami azolar soni: > {all_subscriber}")


# Kanallar bo'limi
@router.message(F.text == '🔧Kanallar', F.chat.type == ChatType.PRIVATE, F.from_user.id == 7634626544)
async def new(msg: Message):
    await msg.answer("Tanlang", reply_markup=await AdminPanel.admin_channel())


@router.message(F.text == "🔙Orqaga qaytish", F.chat.type == ChatType.PRIVATE, F.from_user.id == 7634626544, Form.ch_add or Form.ch_delete)
async def backs(message: Message, state: FSMContext):
    await message.reply("Orqaga qaytildi", reply_markup=await AdminPanel.admin_channel())
    await state.clear()


@router.message(F.text == "➕Kanal qo'shish", F.chat.type == ChatType.PRIVATE, F.from_user.id == 7634626544)
async def channel_add(message: Message, state: FSMContext):
    await message.reply("Kanal qo'shish uchun kanalning userini yuboring.\nMisol uchun @coder_admin",
                        reply_markup=markup)
    await state.set_state(Form.ch_add)


@router.message(Form.ch_add, F.chat.type == ChatType.PRIVATE, F.from_user.id == 7634626544)
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


@router.message(F.text == "❌Kanalni olib tashlash", F.chat.type == ChatType.PRIVATE, F.from_user.id == 7634626544)
async def channel_delete(message: Message, state: FSMContext):
    await message.reply("O'chiriladigan kanalning userini yuboring.\nMisol uchun @coder_admin", reply_markup=markup)
    await state.set_state(Form.ch_delete)


@router.message(Form.ch_delete, F.chat.type == ChatType.PRIVATE, F.from_user.id == 7634626544)
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


@router.message(F.text == "📋 Kanallar ro'yxati", F.chat.type == ChatType.PRIVATE, F.from_user.id == 7634626544)
async def channel_list(message: Message):
    if len(await PanelFunc.channel_list()) > 3:
        await message.reply(await PanelFunc.channel_list())
    else:
        await message.reply("Hozircha kanallar yo'q")
