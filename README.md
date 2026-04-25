👋 Welcome

With this project, you can create your own Telegram bot and generate AI images for free.

To get started, follow the setup steps below:

⚙️ Installation & Setup

Follow these steps to run the bot:

1. Clone the repository

```
git clone https://github.com/gitclone19/freepic.git
cd freepic
```
2. Create virtual environment

```
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```

3. Install dependencies

```
pip install -r requirements.txt
```
---

🤖 Create Telegram Bot (BotFather)

1. Open Telegram and search for **@BotFather**
2. Start the bot and send:
```
/start
```
3. Create a new bot:
```
/newbot
```

4. Enter a name for your bot (e.g. FreePic AI)

5. Enter a username (must end with `bot`, e.g. freepic_ai_bot)

6. Copy the **Bot Token** you receive

---

🔑 Configure Bot

Open your project file:
```
nano bot.py
```

Find this line:
```
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
```

Replace with your real token:
```
TELEGRAM_TOKEN = "123456:ABC-XYZ..."
```
---

▶️ Run the Bot

```
python bot.py
```

If everything is correct, you will see:

Bot started...

---

🎨 Usage

1. Open your bot in Telegram
2. Click **Start**
3. Choose:
   * Model
   * Count
   * Ratio
4. Click **Send a prompt**
5. Enter your prompt (English recommended)

✅ The bot will generate images for you
