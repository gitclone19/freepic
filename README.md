# 🎨 FreePic AI

FreePic AI is a powerful Telegram bot that lets you generate AI images instantly — completely free.

Build your own personal AI image generator and start creating high-quality visuals directly inside Telegram.

---

## 👋 Overview

With FreePic AI, you can:

* Generate AI images in seconds
* Use your own Telegram bot
* Customize generation settings
* Access powerful AI tools without paying

No complex setup. No coding experience required.

---

## ⚙️ Installation & Setup

Follow these steps to run the bot locally:

### 1. Clone the repository

```bash
git clone https://github.com/yoqubov-dev/freepic.git
cd freepic
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🤖 Create Telegram Bot (BotFather)

1. Open Telegram and search for **@BotFather**
2. Send:

```bash
/start
```

3. Create a new bot:

```bash
/newbot
```

4. Set bot name (e.g. **FreePic AI**)
5. Set username (must end with `bot`, e.g. **freepic_ai_bot**)
6. Copy your **Bot Token**

---

## 🔑 Configuration

### 1. Set Telegram Bot Token

Open the bot file:

```bash
nano bot.py
```

Find:

```python
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
```

Replace with your token:

```python
TELEGRAM_TOKEN = "123456:ABC-XYZ..."
```

---

### 2. Configure API Token (.env)

Open or create the `.env` file in the project root:

```bash
nano .env
```

Find:

```env
YOUR_TOKEN=your_api_token_here
```

Now go to:

```
https://infip.pro/
```

Generate your API token from the website and paste it here:

```env
YOUR_TOKEN=your_generated_token_from_infip
```

---

## ▶️ Run the Bot

```bash
python bot.py
```

If everything works:

```
Bot started...
```

---

## 🎨 Usage

1. Open your bot in Telegram
2. Click **Start**
3. Select:

   * Model
   * Image count
   * Aspect ratio
4. Click **Send a prompt**
5. Enter your prompt (English recommended)

✅ The bot will generate AI images instantly.

---

## 🚀 Features

* Fast AI image generation
* Custom prompts
* Multiple models support
* User-friendly interface
* Personal bot control

---

## 📌 Use Cases

* Content creation (Instagram, TikTok)
* Design & creative projects
* AI experimentation
* Personal tools & automation

---

## ⚠️ Notes

* Make sure your bot token is correct
* Keep your tokens private
* Use English prompts for best results

---

## 💡 Future Improvements

* Web dashboard
* More AI models
* Image history
* Advanced customization

---

## 📄 License

This project is open-source and free to use.

---

## ⭐ Support

If you like this project, consider giving it a star on GitHub.

---

**FreePic AI — Your personal AI image generator inside Telegram.**
