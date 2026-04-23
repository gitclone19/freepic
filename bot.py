import logging
import asyncio
import aiohttp
import base64
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# --- TOKEN VA API KEY ---
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
INFIP_API_KEY = "infip-0b40c949"
INFIP_BASE_URL = "https://api.infip.pro"

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)

# --- BOT VA DISPATCHER ---
bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# --- MODELLAR MA'LUMOTLARI ---
# max_count: bu model bir vaqtda nechta rasm chiqaradi
# async_model: True bo'lsa polling kerak
# i2i: image-to-image qo'llab-quvvatlaydi
MODELS = {
    # === TTI MODELLAR (max 4 ta rasm) ===
    "img3": {
        "label": "🌟 Imagen 3",
        "max_count": 4,
        "async_model": False,
        "i2i": False,
        "desc": "Kuchli, tez, universal model"
    },
    "img4": {
        "label": "✨ Imagen 4",
        "max_count": 4,
        "async_model": False,
        "i2i": False,
        "desc": "Eng yangi Imagen, yuqori sifat"
    },
    "qwen": {
        "label": "🎌 Qwen (Anime)",
        "max_count": 4,
        "async_model": True,
        "i2i": False,
        "desc": "Anime va illustratsiya uchun"
    },
    # === TTI MODELLAR (max 1 ta rasm) ===
    "flux-schnell": {
        "label": "⚡ Flux Schnell",
        "max_count": 1,
        "async_model": False,
        "i2i": False,
        "desc": "Ultra tez generatsiya"
    },
    "flux2-dev": {
        "label": "🔬 Flux 2 Dev",
        "max_count": 1,
        "async_model": False,
        "i2i": False,
        "desc": "Fotorealistik, yuqori sifat"
    },
    "flux2-klein-9b": {
        "label": "🧠 Flux 2 Klein 9B",
        "max_count": 1,
        "async_model": False,
        "i2i": False,
        "desc": "9B parametrli kuchli model"
    },
    "flux2-klein-4b": {
        "label": "⚙️ Flux 2 Klein 4B",
        "max_count": 1,
        "async_model": False,
        "i2i": False,
        "desc": "Tez va sifatli 4B model"
    },
    "lucid-origin": {
        "label": "🌀 Lucid Origin",
        "max_count": 1,
        "async_model": False,
        "i2i": False,
        "desc": "Ijodiy, orzuvor uslub"
    },
    "phoenix": {
        "label": "🔥 Phoenix",
        "max_count": 1,
        "async_model": False,
        "i2i": False,
        "desc": "Yuqori sifat va izchillik"
    },
    "sdxl": {
        "label": "🏆 SDXL",
        "max_count": 1,
        "async_model": False,
        "i2i": False,
        "desc": "Professional darajali standart"
    },
    "sdxl-lite": {
        "label": "💨 SDXL Lite",
        "max_count": 1,
        "async_model": False,
        "i2i": False,
        "desc": "SDXL ning tezroq versiyasi"
    },
    "dreamshaper": {
        "label": "🌙 Dreamshaper",
        "max_count": 1,
        "async_model": False,
        "i2i": False,
        "desc": "Orzuvor manzaralar"
    },
    "midjourney": {
        "label": "🎨 Midjourney",
        "max_count": 1,
        "async_model": False,
        "i2i": False,
        "desc": "Badiiy sifat, rassom uslubi"
    },
    "z-image-turbo": {
        "label": "🚀 Z-Image Turbo",
        "max_count": 1,
        "async_model": True,
        "i2i": False,
        "desc": "Chaqmoq tez async model"
    },
    # === ITI MODELLAR — faqat shu 2 ta /v1/images/edits ni qo'llab-quvvatlaydi ===
    "nano-banana": {
        "label": "🍌 Nano Banana",
        "max_count": 1,
        "async_model": True,
        "i2i": True,
        "desc": "ITI uchun flagman model (async)"
    },
    "nbpro": {
        "label": "🍌 Nano Banana Pro",
        "max_count": 1,
        "async_model": True,
        "i2i": True,
        "desc": "ITI uchun premium model (async)"
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
        "mode": "tti",          # tti yoki iti
        "waiting_prompt": False,
        "waiting_image": False,
        "model": "img3",
        "count": 1,
        "ratio": "1:1",
        "pending_image_b64": None,  # ITI uchun
        "nav": "main",           # qaysi menyuda turganini bilish uchun
    }

user_states = {}

# --- KLAVIATURALAR ---

def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🖼 Model"), KeyboardButton(text="🔢 Count")],
            [KeyboardButton(text="📐 Ratio"), KeyboardButton(text="⚙️ Settings")],
            [KeyboardButton(text="🔄 TTI / ITI rejim")],
            [KeyboardButton(text="📝 Prompt yubor")],
        ],
        resize_keyboard=True
    )

def model_keyboard():
    """Barcha modellarni 2-ustunli klaviatura sifatida ko'rsatish"""
    model_keys = list(MODELS.keys())
    rows = []
    for i in range(0, len(model_keys), 2):
        row = [KeyboardButton(text=f"🔸 {MODELS[model_keys[i]]['label']}")]
        if i + 1 < len(model_keys):
            row.append(KeyboardButton(text=f"🔸 {MODELS[model_keys[i+1]]['label']}"))
        rows.append(row)
    rows.append([KeyboardButton(text="⬅️ Orqaga")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

def count_keyboard(model_key: str):
    """Modelga mos max count tugmalarini yaratish"""
    max_n = MODELS[model_key]["max_count"]
    btns = [KeyboardButton(text=str(i)) for i in range(1, max_n + 1)]
    rows = [btns, [KeyboardButton(text="⬅️ Orqaga")]]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

def ratio_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⬜ 1:1"), KeyboardButton(text="📺 16:9"), KeyboardButton(text="📱 9:16")],
            [KeyboardButton(text="⬅️ Orqaga")]
        ],
        resize_keyboard=True
    )

def mode_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✏️ TTI (Matndan rasm)"), KeyboardButton(text="🖼 ITI (Rasmdan rasm)")],
            [KeyboardButton(text="⬅️ Orqaga")]
        ],
        resize_keyboard=True
    )

# --- YORDAMCHI FUNKSIYALAR ---

def get_state(user_id):
    if user_id not in user_states:
        user_states[user_id] = default_state()
    return user_states[user_id]

def find_model_by_label(text: str):
    """Tugma matni bo'yicha model key topish"""
    clean = text.replace("🔸 ", "").strip()
    for key, val in MODELS.items():
        if val["label"] == clean:
            return key
    return None

async def poll_task(task_id: str, session: aiohttp.ClientSession, timeout=120) -> list:
    """Async modellar uchun polling"""
    headers = {"Authorization": f"Bearer {INFIP_API_KEY}"}
    poll_url = f"{INFIP_BASE_URL}/v1/tasks/{task_id}"
    elapsed = 0
    while elapsed < timeout:
        await asyncio.sleep(5)
        elapsed += 5
        async with session.get(poll_url, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                status = data.get("status", "")
                if status == "completed":
                    images = data.get("images") or data.get("data") or []
                    return images
                elif status == "failed":
                    return []
    return []

async def generate_images_tti(state: dict, prompt: str) -> list:
    """TTI: matndan rasm generatsiya qilish"""
    model_key = state["model"]
    model_info = MODELS[model_key]
    size = RATIO_TO_SIZE[state["ratio"]]
    count = min(state["count"], model_info["max_count"])

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

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{INFIP_BASE_URL}/v1/images/generations",
            headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=90)
        ) as resp:
            if resp.status != 200:
                return []
            result = await resp.json()

        # Async model bo'lsa
        if "task_id" in result:
            task_id = result["task_id"]
            images = await poll_task(task_id, session)
        else:
            images = result.get("data") or result.get("images") or []

    urls = []
    for img in images:
        url = img.get("url") if isinstance(img, dict) else img
        if url:
            urls.append(url)
    return urls

async def generate_images_iti(state: dict, prompt: str) -> list:
    """ITI: rasmdan rasm generatsiya qilish"""
    model_key = state["model"]
    image_b64 = state.get("pending_image_b64")
    if not image_b64:
        return []

    size = RATIO_TO_SIZE[state["ratio"]]

    headers = {
        "Authorization": f"Bearer {INFIP_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_key,
        "prompt": prompt,
        "image": image_b64,
        "size": size,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{INFIP_BASE_URL}/v1/images/edits",
            headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=120)
        ) as resp:
            if resp.status != 200:
                return []
            result = await resp.json()

        if "task_id" in result:
            task_id = result["task_id"]
            images = await poll_task(task_id, session)
        else:
            images = result.get("data") or result.get("images") or []

    urls = []
    for img in images:
        url = img.get("url") if isinstance(img, dict) else img
        if url:
            urls.append(url)
    return urls

# --- HANDLERLAR ---

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user_states[message.from_user.id] = default_state()
    await message.answer(
        "👋 Salom! Men <b>FreePic AI</b> botman.\n\n"
        "🎨 Matndan rasm (TTI) va rasmdan rasm (ITI) yaratamanman.\n"
        "Quyidagi tugmalardan foydalaning:",
        reply_markup=main_keyboard()
    )

@dp.message(F.text == "⬅️ Orqaga")
async def back_handler(message: types.Message):
    state = get_state(message.from_user.id)
    state["waiting_prompt"] = False
    state["waiting_image"] = False
    state["nav"] = "main"
    await message.answer("🏠 Asosiy menyu", reply_markup=main_keyboard())

@dp.message(F.text == "🖼 Model")
async def model_menu(message: types.Message):
    state = get_state(message.from_user.id)
    state["nav"] = "model"
    current = MODELS[state["model"]]["label"]
    mode = state["mode"]
    iti_warning = ""
    if mode == "iti":
        iti_warning = "\n\n⚠️ <b>ITI rejim aktiv!</b> Faqat 🍌 Nano Banana va 🍌 Nano Banana Pro ITI ni qo'llab-quvvatlaydi."
    model_list = "\n".join([
        f"• <b>{v['label']}</b> — {v['desc']} | max {v['max_count']} rasm {'| ✏️ITI' if v['i2i'] else ''}"
        for v in MODELS.values()
    ])
    await message.answer(
        f"🤖 <b>Modelni tanlang</b>\n"
        f"Hozirgi: <b>{current}</b>{iti_warning}\n\n"
        "━━━━━━━━━━━━━━━━\n" + model_list,
        reply_markup=model_keyboard()
    )

@dp.message(F.text == "🔢 Count")
async def count_menu(message: types.Message):
    state = get_state(message.from_user.id)
    model_key = state["model"]
    model_info = MODELS[model_key]
    state["nav"] = "count"
    await message.answer(
        f"🔢 <b>Rasm sonini tanlang</b>\n"
        f"Model: <b>{model_info['label']}</b>\n"
        f"Bu model maksimal <b>{model_info['max_count']}</b> ta rasm chiqara oladi:",
        reply_markup=count_keyboard(model_key)
    )

@dp.message(F.text == "📐 Ratio")
async def ratio_menu(message: types.Message):
    state = get_state(message.from_user.id)
    state["nav"] = "ratio"
    await message.answer(
        f"📐 <b>Format (Ratio) tanlang</b>\n"
        f"Hozirgi: <b>{state['ratio']}</b>",
        reply_markup=ratio_keyboard()
    )

@dp.message(F.text == "⚙️ Settings")
async def settings_menu(message: types.Message):
    state = get_state(message.from_user.id)
    model_key = state["model"]
    model_info = MODELS[model_key]
    mode_text = "✏️ Matndan rasm (TTI)" if state["mode"] == "tti" else "🖼 Rasmdan rasm (ITI)"
    await message.answer(
        f"⚙️ <b>Hozirgi sozlamalar:</b>\n\n"
        f"🤖 Model: <b>{model_info['label']}</b>\n"
        f"📝 Tavsif: {model_info['desc']}\n"
        f"🔢 Rasm soni: <b>{state['count']}</b> (max: {model_info['max_count']})\n"
        f"📐 Ratio: <b>{state['ratio']}</b> ({RATIO_TO_SIZE[state['ratio']]})\n"
        f"🔄 Rejim: <b>{mode_text}</b>\n"
        f"⚡ Async: {'Ha' if model_info['async_model'] else 'Yo`q'}",
        reply_markup=main_keyboard()
    )

@dp.message(F.text == "🔄 TTI / ITI rejim")
async def mode_menu(message: types.Message):
    state = get_state(message.from_user.id)
    state["nav"] = "mode"
    current = "TTI (Matndan rasm)" if state["mode"] == "tti" else "ITI (Rasmdan rasm)"
    await message.answer(
        f"🔄 <b>Rejimni tanlang</b>\n"
        f"Hozirgi: <b>{current}</b>\n\n"
        "• <b>TTI</b> — Matn yozing, rasm oling\n"
        "• <b>ITI</b> — Rasm yuboring + matn, yangi rasm oling",
        reply_markup=mode_keyboard()
    )

@dp.message(F.text == "✏️ TTI (Matndan rasm)")
async def set_mode_tti(message: types.Message):
    state = get_state(message.from_user.id)
    state["mode"] = "tti"
    state["nav"] = "main"
    await message.answer("✅ <b>TTI rejim</b> tanlandi.\n📝 Prompt yuborish uchun <b>Prompt yubor</b> tugmasini bosing.", reply_markup=main_keyboard())

@dp.message(F.text == "🖼 ITI (Rasmdan rasm)")
async def set_mode_iti(message: types.Message):
    state = get_state(message.from_user.id)
    state["mode"] = "iti"
    state["nav"] = "main"
    # Agar tanlangan model ITI ni qo'llab-quvvatlamasa, avtomatik nano-banana ga o'tkazish
    current_model = state["model"]
    switched_msg = ""
    if not MODELS[current_model]["i2i"]:
        state["model"] = "nano-banana"
        state["count"] = 1
        switched_msg = (
            "\n\n⚠️ <b>Diqqat:</b> Avvalgi modelingiz (<b>"
            + MODELS[current_model]["label"]
            + "</b>) ITI ni qo'llab-quvvatlamaydi.\n"
            "Avtomatik ravishda <b>🍌 Nano Banana</b> modeliga o'tildi.\n"
            "ITI uchun faqat <b>Nano Banana</b> yoki <b>Nano Banana Pro</b> ishlatilishi mumkin."
        )
    await message.answer(
        "✅ <b>ITI rejim</b> tanlandi.\n"
        "📸 Avval rasm yuboring, so'ng prompt kiriting."
        + switched_msg,
        reply_markup=main_keyboard()
    )

@dp.message(F.text == "📝 Prompt yubor")
async def prompt_btn(message: types.Message):
    state = get_state(message.from_user.id)
    if state["mode"] == "iti" and not state.get("pending_image_b64"):
        state["waiting_image"] = True
        state["waiting_prompt"] = False
        await message.answer("📸 Avval <b>rasmingizni yuboring</b>:", reply_markup=main_keyboard())
    else:
        state["waiting_prompt"] = True
        state["waiting_image"] = False
        await message.answer("📝 <b>Promptingizni yozing</b> (inglizcha yaxshi natija beradi):")

# --- RATIO TUGMALARI ---
@dp.message(F.text.in_(["⬜ 1:1", "📺 16:9", "📱 9:16"]))
async def set_ratio(message: types.Message):
    state = get_state(message.from_user.id)
    ratio_map = {"⬜ 1:1": "1:1", "📺 16:9": "16:9", "📱 9:16": "9:16"}
    ratio = ratio_map[message.text]
    state["ratio"] = ratio
    state["nav"] = "main"
    await message.answer(f"✅ Format tanlandi: <b>{ratio}</b> ({RATIO_TO_SIZE[ratio]})", reply_markup=main_keyboard())

# --- COUNT TUGMALARI (1, 2, 3, 4) ---
@dp.message(F.text.in_(["1", "2", "3", "4"]))
async def set_count(message: types.Message):
    state = get_state(message.from_user.id)
    if state.get("nav") != "count":
        # count menyusida emas, prompt sifatida qabul qilish
        await handle_prompt_text(message)
        return
    n = int(message.text)
    model_key = state["model"]
    max_n = MODELS[model_key]["max_count"]
    if n > max_n:
        await message.answer(f"⚠️ Bu model maksimal <b>{max_n}</b> ta rasm chiqara oladi!")
        return
    state["count"] = n
    state["nav"] = "main"
    await message.answer(f"✅ Rasm soni tanlandi: <b>{n}</b>", reply_markup=main_keyboard())

# --- MODEL TUGMALARI ---
@dp.message(F.text.startswith("🔸 "))
async def set_model(message: types.Message):
    state = get_state(message.from_user.id)
    model_key = find_model_by_label(message.text)
    if not model_key:
        await message.answer("❓ Model topilmadi.")
        return
    state["model"] = model_key
    # count ni model max ga moslashtirish
    if state["count"] > MODELS[model_key]["max_count"]:
        state["count"] = MODELS[model_key]["max_count"]
    state["nav"] = "main"
    info = MODELS[model_key]
    # ITI rejimda ITI qo'llab-quvvatlamasa ogohlantir
    iti_warn = ""
    if state["mode"] == "iti" and not info["i2i"]:
        state["mode"] = "tti"
        iti_warn = "\n\n⚠️ Bu model ITI ni qo'llab-quvvatlamaydi! Rejim avtomatik <b>TTI</b> ga o'zgartirildi."
    await message.answer(
        f"✅ Model tanlandi: <b>{info['label']}</b>\n"
        f"📝 {info['desc']}\n"
        f"🔢 Max rasm: <b>{info['max_count']}</b>\n"
        f"⚡ Async: {'Ha (biroz ko`proq kutiladi)' if info['async_model'] else 'Yo`q (tez)'}"
        f"{'  |  ✏️ ITI qo`llab-quvvatlaydi' if info['i2i'] else ''}"
        + iti_warn,
        reply_markup=main_keyboard()
    )

# --- RASM QABUL QILISH (ITI uchun) ---
@dp.message(F.photo)
async def handle_photo(message: types.Message):
    state = get_state(message.from_user.id)
    if state["mode"] != "iti":
        await message.answer("ℹ️ ITI rejimda emassiz. <b>🔄 TTI / ITI rejim</b> tugmasini bosib ITI ni tanlang.")
        return

    # Rasmni yuklab base64 ga o'tkazish
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_bytes = await bot.download_file(file.file_path)
    img_data = file_bytes.read()
    b64 = base64.b64encode(img_data).decode("utf-8")
    state["pending_image_b64"] = b64
    state["waiting_image"] = False
    state["waiting_prompt"] = True
    await message.answer("✅ Rasm qabul qilindi!\n📝 Endi <b>promptingizni yuboring</b>:")

# --- PROMPT MATN QABUL QILISH ---
async def handle_prompt_text(message: types.Message):
    state = get_state(message.from_user.id)
    prompt = message.text
    state["waiting_prompt"] = False
    model_key = state["model"]
    model_info = MODELS[model_key]
    mode = state["mode"]

    # ITI rejimda rasm bo'lishi shart
    if mode == "iti" and not state.get("pending_image_b64"):
        await message.answer("⚠️ Avval rasm yuboring!")
        state["waiting_image"] = True
        return

    async_note = " (natijani kutish biroz ko'proq vaqt olishi mumkin)" if model_info["async_model"] else ""
    await message.answer(
        f"⏳ <b>Rasm tayyorlanmoqda{async_note}...</b>\n"
        f"🤖 Model: {model_info['label']}\n"
        f"🔢 Soni: {state['count']}\n"
        f"📐 Ratio: {state['ratio']}"
    )

    try:
        if mode == "tti":
            urls = await generate_images_tti(state, prompt)
        else:
            urls = await generate_images_iti(state, prompt)

        if urls:
            for i, url in enumerate(urls):
                caption = f"✅ Tayyor! ({i+1}/{len(urls)})\n🤖 {model_info['label']}" if len(urls) > 1 else f"✅ Tayyor!\n🤖 {model_info['label']}"
                await message.answer_photo(photo=url, caption=caption)
            # ITI rejimda rasmni tozalash
            if mode == "iti":
                state["pending_image_b64"] = None
        else:
            await message.answer("⚠️ Rasm yaratishda xatolik yuz berdi. Boshqa model yoki prompt sinab ko'ring.")
    except asyncio.TimeoutError:
        await message.answer("⏱ Vaqt tugadi. Model hozir band bo'lishi mumkin, keyinroq urinib ko'ring.")
    except Exception as e:
        logging.error(f"Xato: {e}")
        await message.answer(f"❌ Xatolik yuz berdi:\n<code>{str(e)[:200]}</code>")

@dp.message()
async def handle_message(message: types.Message):
    state = get_state(message.from_user.id)
    text = message.text or ""

    if state.get("waiting_prompt") and text:
        await handle_prompt_text(message)
        return

    if state.get("waiting_image"):
        await message.answer("📸 Iltimos, <b>rasm yuboring</b> (matn emas).")
        return

    await message.answer("❓ Tugmalardan foydalaning.", reply_markup=main_keyboard())


# --- BOTNI ISHGA TUSHURISH ---
async def main():
    logging.info("Bot ishga tushirildi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
