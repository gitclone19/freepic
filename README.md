🎨 FreePic AI — Telegram Bot

A Telegram bot for generating images using AI. Powered by the infip.pro
 API.
Supports both TTI (text-to-image) and ITI (image-to-image) modes.

📋 Requirements
Python 3.10+
Telegram Bot Token (get it via BotFather
)
Infip API Key (get it from infip.pro/api-keys
)
⚙️ Installation
1. Clone the repository
git clone https://github.com/your-repo/freepic-bot.git
cd freepic-bot
2. Install dependencies
pip install -r requirements.txt
3. Configure tokens and API keys

Open bot.py and replace the following lines:

TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
INFIP_API_KEY  = "YOUR_INFIP_API_KEY"
4. Run the bot
python bot.py
🤖 Models
TTI Models (Text-to-Image)
Model	Name	Max Images	Speed
img3	🌟 Imagen 3	4	Fast
img4	✨ Imagen 4	4	Fast
qwen	🎌 Qwen (Anime)	4	Async
flux-schnell	⚡ Flux Schnell	1	Ultra fast
flux2-dev	🔬 Flux 2 Dev	1	Fast
flux2-klein-9b	🧠 Flux 2 Klein 9B	1	Fast
flux2-klein-4b	⚙️ Flux 2 Klein 4B	1	Fast
lucid-origin	🌀 Lucid Origin	1	Fast
phoenix	🔥 Phoenix	1	Fast
sdxl	🏆 SDXL	1	Fast
sdxl-lite	💨 SDXL Lite	1	Fast
dreamshaper	🌙 Dreamshaper	1	Fast
midjourney	🎨 Midjourney	1	Fast
z-image-turbo	🚀 Z-Image Turbo	1	Async
ITI Models (Image-to-Image)
Model	Name	Max Images	Speed
nano-banana	🍌 Nano Banana	1	Async
nbpro	🍌 Nano Banana Pro	1	Async

⚠️ ITI mode works only with nano-banana and nbpro.

🕹️ Usage
Main buttons
Button	Function
🖼 Model	Select AI model
🔢 Count	Choose number of images (1–4 depending on model)
📐 Ratio	Select image size
⚙️ Settings	View current settings
🔄 TTI / ITI mode	Switch mode
📝 Send Prompt	Start image generation
Ratio options
Button	Ratio	Size
⬜ 1:1	Square	1024×1024
📺 16:9	Landscape	1792×1024
📱 9:16	Portrait	1024×1792
🔄 TTI vs ITI
✏️ TTI — Text to Image
Select 🔄 TTI / ITI mode → ✏️ TTI
Configure Model, Count, and Ratio
Click 📝 Send Prompt
Enter your prompt (English gives better results)
Image is ready ✅
🖼 ITI — Image to Image
Select 🔄 TTI / ITI mode → 🖼 ITI
(model automatically switches to Nano Banana)
Click 📝 Send Prompt
Upload your image
After upload, enter your prompt
Modified image is ready ✅
⚡ About Async Models

Models like qwen, nano-banana, nbpro, z-image-turbo work asynchronously — results may take 10–60 seconds. The bot automatically polls and retrieves the result.

📁 File Structure
freepic-bot/
├── bot.py           # Main bot code
├── requirements.txt # Dependencies
└── README.md        # This file
📦 requirements.txt
aiogram==3.7.0
aiohttp==3.9.5
🛠️ Errors and Solutions
Error	Cause	Solution
⚠️ Image generation error	Invalid model or prompt	Try another model or prompt
⏱ Timeout	Server busy or slow	Wait and try again
ITI not working	Wrong model selected	Use only Nano Banana or Nano Banana Pro
401 Unauthorized	Invalid API key	Check INFIP_API_KEY
📌 Important Notes
Free limit: 30 requests/minute, 1000 requests/day
Prompt language: English prompts give better results
ITI mode: Only works with nano-banana and nbpro
Async models: Results take 10–60 seconds

🔗 Useful Links
https://infip.pro — API base
https://infip.pro/models — All models
https://infip.pro/api-keys — Get API key
https://t.me/BotFather — Get Telegram bot token
https://docs.aiogram.dev — aiogram documentation
