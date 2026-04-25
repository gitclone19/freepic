import logging
import asyncio
import aiohttp
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# --- TOKEN ---
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"


def _load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())

_load_env()

INFIP_API_KEY = os.environ["INFIP_API_KEY"]
INFIP_BASE_URL = os.environ["INFIP_BASE_URL"]

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)

# --- BOT AND DISPATCHER ---
bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# --- MODEL DATA ---
MODELS = {
    "img3": {
        "label": "🌟 Imagen 3",
        "max_count": 4,
        "desc": "Kuchli, tez, universal model"
    },
    "img4": {
        "label": "✨ Imagen 4",
        "max_count": 4,
        "desc": "Eng yangi Imagen, yuqori sifat"
    },
}

# Ratio → size mapping
RATIO_TO_SIZE = {
    "1:1": "1024x1024",
    "16:9": "1792x1024",
    "9:16": "1024x1792",
}

# --- DEFAULT USER STATE ---
def default_state():
    return {
        "waiting_prompt": False,
        "model": "img3",
        "count": 1,
        "ratio": "1:1",
    }

user_states = {}

# --- KEYBOARDS ---

def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🖼 Model"), KeyboardButton(text="🔢 Count")],
            [KeyboardButton(text="📐 Ratio")],
            [KeyboardButton(text="📝 Send a prompt")],
        ],
        resize_keyboard=True
    )

def model_keyboard():
    rows = []
    for key, model in MODELS.items():
        rows.append([KeyboardButton(text=f"🔸 {model['label']}")])
    rows.append([KeyboardButton(text="🌐 Other models")])
    rows.append([KeyboardButton(text="⬅️ Back")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

def count_keyboard():
    btns = [KeyboardButton(text=str(i)) for i in range(1, 5)]
    return ReplyKeyboardMarkup(
        keyboard=[btns, [KeyboardButton(text="⬅️ Back")]],
        resize_keyboard=True
    )

def ratio_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⬜ 1:1"), KeyboardButton(text="📺 16:9"), KeyboardButton(text="📱 9:16")],
            [KeyboardButton(text="⬅️ Back")]
        ],
        resize_keyboard=True
    )

# --- HELPER FUNCTIONS ---

def get_state(user_id):
    if user_id not in user_states:
        user_states[user_id] = default_state()
    return user_states[user_id]

def find_model_by_label(text: str):
    clean = text.replace("🔸 ", "").strip()
    for key, val in MODELS.items():
        if val["label"] == clean:
            return key
    return None

async def generate_images(state: dict, prompt: str) -> list:
    model_key = state["model"]
    model_info = MODELS[model_key]
    size = RATIO_TO_SIZE[state["ratio"]]
    count = state["count"]

    headers = {
        "Authorization": f"Bearer {INFIP_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model_key,
        "prompt": prompt,
        "n": count,
        "size": size,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{INFIP_BASE_URL}/v1/images/generations",
                headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=120)
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    logging.error(f"API Error ({resp.status}): {error_text}")
                    return []
                result = await resp.json()

            images = result.get("data") or result.get("images") or []

        urls = []
        for img in images:
            url = img.get("url") if isinstance(img, dict) else img
            if url:
                urls.append(url)
        return urls
    except asyncio.TimeoutError:
        logging.error("Request timeout")
        return []
    except Exception as e:
        logging.error(f"Generate error: {e}")
        return []

# --- HANDLERLAR ---

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user_states[message.from_user.id] = default_state()
    await message.answer(
        "👋 Hello! I am the <b>FreePic AI</b> bot.\n\n"
        "🎨 I generate images from text (TTI).\n"
        "Use the buttons below:",
        reply_markup=main_keyboard()
    )

@dp.message(F.text == "⬅️ Back")
async def back_handler(message: types.Message):
    state = get_state(message.from_user.id)
    state["waiting_prompt"] = False
    await message.answer("🏠 Main Menu", reply_markup=main_keyboard())

@dp.message(F.text == "🖼 Model")
async def model_menu(message: types.Message):
    state = get_state(message.from_user.id)
    current = MODELS[state["model"]]["label"]
    model_list = "\n".join([
        f"• <b>{v['label']}</b> — {v['desc']}"
        for v in MODELS.values()
    ])
    await message.answer(
        f"🤖 <b>Select a model</b>\n"
        f"Current model: <b>{current}</b>\n\n"
        "━━━━━━━━━━━━━━━━\n" + model_list,
        reply_markup=model_keyboard()
    )

@dp.message(F.text == "🔢 Count")
async def count_menu(message: types.Message):
    state = get_state(message.from_user.id)
    model_key = state["model"]
    model_info = MODELS[model_key]
    await message.answer(
        f"🔢 <b>Select the number of images</b>\n"
        f"Model: <b>{model_info['label']}</b>\n"
        f"This model can generate a maximum of <b>4</b> images:",
        reply_markup=count_keyboard()
    )

@dp.message(F.text == "📐 Ratio")
async def ratio_menu(message: types.Message):
    state = get_state(message.from_user.id)
    await message.answer(
        f"📐 <b>Select a format (Ratio)</b>\n"
        f"Current ratio: <b>{state['ratio']}</b>",
        reply_markup=ratio_keyboard()
    )

@dp.message(F.text == "📝 Send a prompt")
async def prompt_btn(message: types.Message):
    state = get_state(message.from_user.id)
    state["waiting_prompt"] = True
    await message.answer("📝 <b>Enter your prompt</b> (English gives better results):")

@dp.message(F.text.in_(["⬜ 1:1", "📺 16:9", "📱 9:16"]))
async def set_ratio(message: types.Message):
    state = get_state(message.from_user.id)
    ratio_map = {"⬜ 1:1": "1:1", "📺 16:9": "16:9", "📱 9:16": "9:16"}
    ratio = ratio_map[message.text]
    state["ratio"] = ratio
    await message.answer(f"✅ Format selected: <b>{ratio}</b> ({RATIO_TO_SIZE[ratio]})", reply_markup=main_keyboard())

@dp.message(F.text.in_(["1", "2", "3", "4"]))
async def set_count(message: types.Message):
    state = get_state(message.from_user.id)
    if state.get("waiting_prompt"):
        await handle_prompt_text(message)
        return
    n = int(message.text)
    state["count"] = n
    await message.answer(f"✅ Number of images selected: <b>{n}</b>", reply_markup=main_keyboard())

@dp.message(F.text.startswith("🔸 "))
async def set_model(message: types.Message):
    state = get_state(message.from_user.id)
    model_key = find_model_by_label(message.text)
    if not model_key:
        await message.answer("❓ Model not found.")
        return
    state["model"] = model_key
    info = MODELS[model_key]
    await message.answer(
        f"✅ Model selected: <b>{info['label']}</b>\n"
        f"📝 {info['desc']}",
        reply_markup=main_keyboard()
    )

@dp.message(F.text == "🌐 Other models")
async def other_models(message: types.Message):
    await message.answer("Other models 👉 https://infip.pro/")

async def handle_prompt_text(message: types.Message):
    state = get_state(message.from_user.id)
    prompt = message.text
    state["waiting_prompt"] = False
    model_key = state["model"]
    model_info = MODELS[model_key]

    await message.answer(
        f"⏳ <b>Generating image...</b>\n"
        f"🤖 Model: {model_info['label']}\n"
        f"🔢 Count: {state['count']}\n"
        f"📐 Ratio: {state['ratio']}"
    )

    try:
        urls = await generate_images(state, prompt)
        if urls:
            for i, url in enumerate(urls):
                caption = f"✅ Done! ({i+1}/{len(urls)})\n🤖 {model_info['label']}" if len(urls) > 1 else f"✅ Done!\n🤖 {model_info['label']}"
                await message.answer_photo(photo=url, caption=caption)
        else:
            await message.answer("⚠️ An error occurred while generating the image.\n\n💡 To fix the issue:\n• Check that your API key is correct\n• Try a different prompt\n• Wait a few seconds and try again")
    except asyncio.TimeoutError:
        await message.answer("⏱ Time is up. The model may be busy right now, please try again later.")
    except Exception as e:
        logging.error(f"Error: {e}")
        await message.answer(f"❌ An error occurred:\n<code>{str(e)[:200]}</code>")
    finally:
        await message.answer("🏠 Main Menu", reply_markup=main_keyboard())

@dp.message()
async def handle_message(message: types.Message):
    state = get_state(message.from_user.id)
    if state.get("waiting_prompt"):
        await handle_prompt_text(message)
        return
    await message.answer("❓ Use the buttons.", reply_markup=main_keyboard())

# --- START THE BOT ---
async def main():
    logging.info("Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
