import logging
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# --- TOKEN VA API KEY ---
TELEGRAM_TOKEN = "8353148771:AAFyblzo0j5GybhmcTunwStdlmcZAMiNo08"
INFIP_API_KEY = "infip-26bacb20"
INFIP_API_URL = "https://api.infip.pro/v1/images/generations"

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)

# --- BOT VA DISPATCHER ---
bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# --- USER STATES ---
user_states = {}

# --- ASOSIY KLAVIATURA ---
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🖼 Model"), KeyboardButton(text="🔢 Count")],
        [KeyboardButton(text="📐 Ratio"), KeyboardButton(text="⚙️ Settings")],
        [KeyboardButton(text="📝 Prompt")]
    ],
    resize_keyboard=True
)

# --- START KOMANDASI ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user_states[message.from_user.id] = {
        "waiting_prompt": False,
        "model": "img3",
        "count": 1,
        "size": "1024x1024"
    }
    await message.answer(
        "Salom Aka! Men FreePic AI botman.\nQuyidagi tugmalardan foydalaning:",
        reply_markup=main_keyboard
    )

# --- TUGMA LOGIKASI ---
@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    text = message.text
    state = user_states.setdefault(user_id, {"waiting_prompt": False, "model": "img3", "count": 1, "size": "1024x1024"})

    # PROMPT
    if text == "📝 Prompt":
        state["waiting_prompt"] = True
        await message.answer("Prompt yuboring:")
        return

    # MODEL TANLASH
    if text == "🖼 Model":
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="img3"), KeyboardButton(text="img4")],
                [KeyboardButton(text="qwen")],
                [KeyboardButton(text="⬅️ Orqaga")]
            ], resize_keyboard=True
        )
        await message.answer("Modelni tanlang:", reply_markup=kb)
        return
    if text in ["img3", "img4", "qwen"]:
        state["model"] = text
        await message.answer(f"✅ Model tanlandi: {text}", reply_markup=main_keyboard)
        return

    # COUNT TANLASH (1 yoki 2 bilan cheklangan)
    if text == "🔢 Count":
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="1"), KeyboardButton(text="2")],
                [KeyboardButton(text="⬅️ Orqaga")]
            ], resize_keyboard=True
        )
        await message.answer("Nechta rasm kerak? (1 yoki 2)", reply_markup=kb)
        return
    if text in ["1", "2"]:
        state["count"] = int(text)
        await message.answer(f"✅ Rasm soni tanlandi: {text}", reply_markup=main_keyboard)
        return

    # RATIO TANLASH
    if text == "📐 Ratio":
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="1:1"), KeyboardButton(text="16:9"), KeyboardButton(text="9:16")],
                [KeyboardButton(text="⬅️ Orqaga")]
            ], resize_keyboard=True
        )
        await message.answer("Formatni tanlang:", reply_markup=kb)
        return
    if text in ["1:1", "16:9", "9:16"]:
        if text == "1:1":
            state["size"] = "1024x1024"
        elif text == "16:9":
            state["size"] = "1792x1024"
        elif text == "9:16":
            state["size"] = "1024x1792"
        await message.answer(f"✅ Format tanlandi: {text}", reply_markup=main_keyboard)
        return

    # SETTINGS
    if text == "⚙️ Settings":
        settings_text = (
            f"⚙️ Hozirgi sozlamalar:\n"
            f"Model: {state.get('model')}\n"
            f"Rasm soni: {state.get('count')}\n"
            f"Format: {state.get('size')}"
        )
        await message.answer(settings_text, reply_markup=main_keyboard)
        return

    # ORQAGA QAYTISH
    if text == "⬅️ Orqaga":
        await message.answer("Asosiy menyu", reply_markup=main_keyboard)
        return

    # PROMPT YUBORILGANIDA (asinxron)
    if state.get("waiting_prompt"):
        prompt = text
        state["waiting_prompt"] = False
        await message.answer("⏳ Rasm tayyorlanmoqda, biroz kuting...")

        headers = {
            "Authorization": f"Bearer {INFIP_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": state["model"],
            "prompt": prompt,
            "n": state["count"],
            "size": state["size"]
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(INFIP_API_URL, headers=headers, json=data, timeout=60) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        images = result.get("images") or result.get("data") or []
                        if images:
                            for img in images:
                                url = img.get("url") if isinstance(img, dict) else img
                                await message.answer_photo(photo=url, caption="✅ Tayyor!")
                        else:
                            await message.answer("⚠️ Rasm tayyorlashda muammo bor.")
                    else:
                        await message.answer(f"❌ Xato: {resp.status}")
            except Exception as e:
                await message.answer(f"⚠️ API bilan bog‘lanishda muammo bor:\n{str(e)}")
        return

    # NOMALUM TUGMA
    await message.answer("❓ Tugmalardan foydalaning.", reply_markup=main_keyboard)


# --- BOTNI ISHGA TUSHURISH ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
