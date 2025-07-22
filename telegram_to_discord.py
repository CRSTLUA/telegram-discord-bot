import asyncio
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

from flask import Flask
from threading import Thread

TELEGRAM_TOKEN = '7833122280:AAGG0fc1bVBLSTD8DAjdkFrBBg88_kDm4gs'
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1396893886294790174/ioWp2uCe1jEp22FktJFqzsyQ1wPTm1zrI8T0kWexYMGF70rgQl0XfEwcuaMsd_XugABp'

app = Flask('')


@app.route('/')
def home():
    return "Bot is running"


def run():
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)


def keep_alive():
    t = Thread(target=run)
    t.start()


def parse_entities(text, entities):
    if not entities:
        return text

    result = ""
    last_offset = 0

    for ent in entities:
        result += text[last_offset:ent.offset]

        if ent.type == 'text_link':
            display_text = text[ent.offset:ent.offset + ent.length]
            result += display_text  # Без посилання
        else:
            result += text[ent.offset:ent.offset + ent.length]

        last_offset = ent.offset + ent.length

    result += text[last_offset:]
    return result



async def forward_to_discord(update: Update,
                             context: ContextTypes.DEFAULT_TYPE):
    print("🚦 Отримано повідомлення з Telegram:", update)

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

    if content:
        print("📤 Відправляю в Discord:", content)
        requests.post(DISCORD_WEBHOOK_URL, json={"content": content})


if __name__ == '__main__':
    keep_alive()  # Запускаємо вебсервер для UptimeRobot

    app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app_bot.add_handler(MessageHandler(filters.ALL, forward_to_discord))

    print("🤖 Бот запущений. Очікую нові повідомлення...")
    app_bot.run_polling()

