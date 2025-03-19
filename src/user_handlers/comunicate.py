from aiogram import F, Router, Bot
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, UNSET_PARSE_MODE


from src.buttons.buttons import UserPanels
from config import GROUP_ID, bot

router: Router = Router()


class From(StatesGroup):
    problem_text = State()
    problem_text2 = State()
    problem_file = State()


@router.message(F.text == "️‼️Fikr bildirish", lambda message: message.chat.type == ChatType.PRIVATE)
async def person_quest(message: Message, state: FSMContext):
    try: await message.delete()
    except: pass
    await message.answer("Savolingiz matnini yuboring", reply_markup=await UserPanels.back_menu())
    await state.set_state(From.problem_text)


@router.message(From.problem_text)
async def person_quest1(message: Message, state: FSMContext):
    msg_text = message.text
    user_id = message.from_user.id
    await state.clear()
    await state.set_state(From.problem_text2)
    if msg_text == "So'rovni tugatish":
        await message.answer("So'rov tugatildi, bosh menyu", reply_markup=await UserPanels.main_manu())
        await state.clear()
    else:
        name = message.from_user.first_name
        msg = await bot.send_message(chat_id=GROUP_ID, text=(str(user_id) + f" - <b>{name}</b>\n @{message.from_user.username}"), parse_mode='html')
        await bot.copy_message(
            chat_id=GROUP_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id,
            reply_to_message_id=msg.message_id)


@router.message(From.problem_text2)
async def person_quest1(message: Message, state: FSMContext):
    msg_text = message.text
    user_id = message.from_user.id
    if msg_text == "So'rovni tugatish":
        await message.answer("So'rov tugatildi, bosh menyu", reply_markup=await UserPanels.main_manu())
        await state.clear()
    else:
        name = message.from_user.first_name
        msg = await bot.send_message(chat_id=GROUP_ID, text=(str(user_id) + f" - <b>{name}</b>\n @{message.from_user.username}"), parse_mode='html')

        await bot.copy_message(
            chat_id=GROUP_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id,
            reply_to_message_id=msg.message_id)


def chat_is():
    async def filter(message: Message):
        return message.chat.type in ["supergroup"] and message.chat.id == GROUP_ID
    return filter


@router.message(chat_is())
async def handling_prob(message: Message):
    if message.reply_to_message and message.reply_to_message.from_user.id == bot.id:
        original_message_text = message.reply_to_message.text
        try:
            await bot.copy_message(chat_id=original_message_text.split(' - ')[0],
                                   from_chat_id=message.chat.id,
                                   message_id=message.message_id)
        except Exception as ex:
            await message.reply("foydalanuvchiga xabar yuborish uchun uni "
                                "ID va ismi berilgan xabarga javob berish kerak\n\n"
                                "agar siz ID li xabarga javob qilgan bo'lsangiz ammo yana bu xabarni ko'rayotgan "
                                "bo'lsangiz katta extimol siz xabarlashmoqchi bo'lgan user botni blocklagan. "
                                "va unga boshqa xabar yubora olmaysiz")

