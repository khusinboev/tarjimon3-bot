import asyncio
from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramAPIError,
    TelegramForbiddenError,
    TelegramNotFound,
)

from config import adminPanel, sql, bot
from src.keyboards.buttons import AdminPanel

msg_router = Router()

# === HOLATLAR (FSM) === #
class Form(StatesGroup):
    forward_msg = State()
    send_msg = State()

# === QAYTISH TUGMASI === #
markup = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[[KeyboardButton(text="🔙Orqaga qaytish")]]
)

# === ADMIN PANELGA KIRISH === #
@msg_router.message(F.text == "✍Xabarlar", F.chat.type == ChatType.PRIVATE, F.from_user.id.in_(adminPanel))
async def panel_handler(message: Message) -> None:
    await message.answer("✍ Xabarlar bo‘limi", reply_markup=await AdminPanel.admin_msg())


# === FORWARD XABAR BOSHLASH === #
@msg_router.message(F.text == "📨Forward xabar yuborish", F.chat.type == ChatType.PRIVATE, F.from_user.id.in_(adminPanel))
async def start_forward(message: Message, state: FSMContext):
    await message.answer("📨 Forward yuboriladigan xabarni yuboring", reply_markup=markup)
    await state.set_state(Form.forward_msg)


# === FORWARD XABARNI YUBORISH === #
@msg_router.message(Form.forward_msg, F.chat.type == ChatType.PRIVATE, F.from_user.id.in_(adminPanel))
async def send_forward_to_all(message: Message, state: FSMContext):
    await state.clear()
    sql.execute("SELECT user_id FROM public.accounts")
    rows = sql.fetchall()
    user_ids = [row[0] for row in rows]

    success, failed = await broadcast_forward(user_ids, message)

    await message.answer(
        f"✅ Forward xabar yuborildi\n\n"
        f"📤 Yuborilgan: {success} ta\n"
        f"❌ Yuborilmagan: {failed} ta",
        reply_markup=await AdminPanel.admin_msg()
    )


# === ODDIY XABAR BOSHLASH === #
@msg_router.message(F.text == "📬Oddiy xabar yuborish", F.chat.type == ChatType.PRIVATE, F.from_user.id.in_(adminPanel))
async def start_text_send(message: Message, state: FSMContext):
    await message.answer("📬 Yuborilishi kerak bo‘lgan matnli xabarni yuboring", reply_markup=markup)
    await state.set_state(Form.send_msg)


# === ODDIY XABARNI YUBORISH === #
@msg_router.message(Form.send_msg, F.chat.type == ChatType.PRIVATE, F.from_user.id.in_(adminPanel))
async def send_text_to_all(message: Message, state: FSMContext):
    await state.clear()
    sql.execute("SELECT user_id FROM public.accounts")
    rows = sql.fetchall()
    user_ids = [row[0] for row in rows]

    success, failed = await broadcast_copy(user_ids, message)

    await message.answer(
        f"✅ Matnli xabar yuborildi\n\n"
        f"📤 Yuborilgan: {success} ta\n"
        f"❌ Yuborilmagan: {failed} ta",
        reply_markup=await AdminPanel.admin_msg()
    )


# === ORQAGA QAYTISH (ikkala holatda ham) === #
@msg_router.message(F.text == "🔙Orqaga qaytish", F.chat.type == ChatType.PRIVATE, F.from_user.id.in_(adminPanel), Form.forward_msg | Form.send_msg)
async def back_to_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("⬅️ Orqaga qaytdingiz", reply_markup=await AdminPanel.admin_msg())


# =======================
#       BROADCAST
# =======================

semaphore = asyncio.Semaphore(30)  # 30 ta parallel yuborish

# --- MATNLI XABAR BROADCAST --- #
async def broadcast_copy(user_ids: list[int], message: Message) -> tuple[int, int]:
    success = 0
    failed = 0
    status_msg = await message.answer("📤 Yuborish boshlandi...")

    for i, user_id in enumerate(user_ids, 1):
        result = await send_copy_safe(user_id, message)
        if result:
            success += 1
        else:
            failed += 1

        if i % 100 == 0 or i == len(user_ids):
            try:
                await status_msg.edit_text(
                    f"📬 Oddiy xabar yuborilmoqda...\n\n"
                    f"✅ Yuborilgan: {success} ta\n"
                    f"❌ Yuborilmagan: {failed} ta\n"
                    f"📦 Jami: {len(user_ids)} ta\n"
                    f"📊 Progres: {i}/{len(user_ids)}"
                )
            except Exception as e:
                print(f"❗Holat yangilashda xato: {e}")
    return success, failed


# --- FORWARD XABAR BROADCAST --- #
async def broadcast_forward(user_ids: list[int], message: Message) -> tuple[int, int]:
    success = 0
    failed = 0
    status_msg = await message.answer("📨 Forward yuborish boshlandi...")

    for i, user_id in enumerate(user_ids, 1):
        result = await send_forward_safe(user_id, message)
        if result:
            success += 1
        else:
            failed += 1

        if i % 100 == 0 or i == len(user_ids):
            try:
                await status_msg.edit_text(
                    f"📨 Forward yuborilmoqda...\n\n"
                    f"✅ Yuborilgan: {success} ta\n"
                    f"❌ Yuborilmagan: {failed} ta\n"
                    f"📦 Jami: {len(user_ids)} ta\n"
                    f"📊 Progres: {i}/{len(user_ids)}"
                )
            except Exception as e:
                print(f"❗Forward holati xato: {e}")
    return success, failed


# === XAVFSIZ COPY FUNKSIYASI === #
async def send_copy_safe(user_id: int, message: Message, retries=3) -> int:
    for attempt in range(retries):
        try:
            async with semaphore:
                await bot.copy_message(
                    chat_id=user_id,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id
                )
                return 1
        except (TelegramForbiddenError, TelegramNotFound, TelegramBadRequest, TelegramAPIError):
            return 0
        except Exception as e:
            print(f"❌ Copy error user_id={user_id} (attempt {attempt + 1}): {e}")
            await asyncio.sleep(1)
    return 0


# === XAVFSIZ FORWARD FUNKSIYASI === #
async def send_forward_safe(user_id: int, message: Message, retries=3) -> int:
    for attempt in range(retries):
        try:
            async with semaphore:
                await bot.forward_message(
                    chat_id=user_id,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id
                )
                return 1
        except (TelegramForbiddenError, TelegramNotFound, TelegramBadRequest, TelegramAPIError):
            return 0
        except Exception as e:
            print(f"❌ Forward error user_id={user_id} (attempt {attempt + 1}): {e}")
            await asyncio.sleep(1)
    return 0