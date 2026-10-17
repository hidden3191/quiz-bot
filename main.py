import os, asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot live hai! /quiz bhejo")

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = "India ka capital kya hai? A) Mumbai B) Delhi C) Kolkata"
    await update.message.reply_text(q)

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": user_text}],
            model="llama3-8b-8192",
        )
        reply = chat_completion.choices[0].message.content
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# Render ko khush rakhne ke liye web server
from flask import Flask
import threading
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Running"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
    print("Bot starting...")
    application.run_polling()
