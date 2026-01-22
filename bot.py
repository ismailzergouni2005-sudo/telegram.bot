import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

BOT_TOKEN = os.getenv("BOT_TOKEN")  # سنضعه في Render لاحقًا
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

pending_photos = {}

@dp.message(Command("start"))
async def start(msg: Message):
    await msg.answer("أرسل صورة وسأقترح عليك لغة البرومبت كل مرة.")

@dp.message(F.photo)
async def ask_language(msg: Message):
    photo = msg.photo[-1]
    pending_photos[msg.from_user.id] = photo.file_id
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="العربية", callback_data="lang:ar")],
        [InlineKeyboardButton(text="English", callback_data="lang:en")]
    ])
    await msg.answer("اختر اللغة التي تريد البرومبت بها:", reply_markup=kb)

@dp.callback_query(F.data.startswith("lang:"))
async def generate_prompt(cb):
    lang = cb.data.split(":")[1]
    photo_id = pending_photos.get(cb.from_user.id)
    if not photo_id:
        await cb.answer("لا توجد صورة محفوظة.")
        return

    # هنا ضع منطق توليد البرومبت من الصورة (BLIP أو غيره)
    prompt_en = "A photo of a cat sitting on a chair."
    prompt_ar = "صورة لقط يجلس على كرسي."
    prompt = prompt_ar if lang == "ar" else prompt_en

    await cb.message.answer(f"البرومبت ({lang}):\n\n{prompt}")
    await cb.answer("تم توليد البرومبت.")
    pending_photos.pop(cb.from_user.id, None)

async def main():
    await dp.start_polling(bot)

if name == "main":
    asyncio.run(main())
