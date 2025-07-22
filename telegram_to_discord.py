import httpx
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
import asyncio
import threading

TELEGRAM_TOKEN = '7833122280:AAGG0fc1bVBLSTD8DAjdkFrBBg88_kDm4gs'
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1396893886294790174/ioWp2uCe1jEp22FktJFqzsyQ1wPTm1zrI8T0kWexYMGF70rgQl0XfEwcuaMsd_XugABp'
WEBHOOK_URL = 'https://telegram-discord-bot-xbca.onrender.com/webhook'

app = Flask(__name__)
application = Application.builder().token(TELEGRAM_TOKEN).build()

BANNED_WORDS = ['𝑪𝑹𝑺𝑻𝑳𝑼𝑨']


def parse_entities(text, entities):
    if not entities:
        return text

    result = ""
    last_offset = 0

    for ent in entities:
        result += text[last_offset:ent.offset]
        result += text[ent.offset:ent.offset + ent.length]
        last_offset = ent.offset + ent.length

    result += text[last_offset:]
    return result


async def forward_to_discord(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.message or update.channel_post
        if not message:
            return

        content = ""

        if message.text:
            content += parse_entities(message.text, message.entities)
        elif message.caption:
            content += parse_entities(message.caption, message.caption_entities)

        if message.photo:
            file = await message.photo[-1].get_file()
            content += f"\n[Фото]({file.file_path})"
        if message.video:
            file = await message.video.get_file()
            content += f"\n[Відео]({file.file_path})"

        for word in BANNED_WORDS:
            content = content.replace(word, '')

        if content.strip():
            print("📤 Відправляю в Discord:", content)
            async with httpx.AsyncClient() as client:
                await client.post(DISCORD_WEBHOOK_URL, json={"content": content})

    except Exception as e:
        print(f"❌ Помилка при обробці повідомлення: {e}")


application.add_handler(MessageHandler(filters.ALL, forward_to_discord))


@app.route('/')
def home():
    return "✅ Bot is running"


@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update_data = request.get_json(force=True)
        update = Update.de_json(update_data, application.bot)
        asyncio.run(application.process_update(update))
    except Exception as e:
        print(f"❌ Webhook помилка: {e}")
    return 'ok', 200


def run_flask():
    app.run(host='0.0.0.0', port=8080)


async def set_webhook():
    await application.initialize()
    await application.start()
    await application.bot.set_webhook(WEBHOOK_URL)
    print("🤖 Webhook встановлено:", WEBHOOK_URL)


if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    asyncio.run(set_webhook())
