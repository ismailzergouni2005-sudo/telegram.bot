import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import google.generativeai as genai

# إعداد التوكنات
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# إعداد Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

pending_photos = {}

@dp.message(Command("start"))
async def start(msg: Message):
    await msg.answer("أرسل صورة وسأقترح عليك برومبت باستخدام Gemini.")

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

    # تحميل الصورة من تيليغرام
    file = await bot.get_file(photo_id)
    photo_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"

    # إرسال الصورة إلى Gemini
    response = model.generate_content([
        {"mime_type": "image/jpeg", "data": photo_url},
        f"اكتب وصف للصورة بلغة {'العربية' if lang == 'ar' else 'English'}"
    ])

    prompt = response.text if response.text else "لم أتمكن من توليد البرومبت."

    await cb.message.answer(f"البرومبت ({lang}):\n\n{prompt}")
    await cb.answer("تم توليد البرومبت.")
    pending_photos.pop(cb.from_user.id, None)

async def main():
    await dp.start_polling(bot)

if name == "main":
    asyncio.run(main())
