import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# लॉग्स देखने के लिए सेटअप (Render पर कोई भी दिक्कत होगी तो यहाँ दिखेगा)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# API Keys लोड करना (इन्हें Render के Environment Variables में डालना अनिवार्य है)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Groq क्लाइंट को शुरू करना
groq_client = Groq(api_key=GROQ_API_KEY)

# 1. /start कमांड का फंक्शन
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "नमस्ते! मैं Groq AI से जुड़ा एक एडवांस टेलीग्राम बॉट हूँ। मुझसे कुछ भी पूछिए!"
    )

# 2. यूजर के मैसेज का जवाब देने का फंक्शन (Groq AI Integration)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    try:
        # Groq API से जवाब मांगना
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": user_text,
                }
            ],
            model="llama3-8b-8192", # सबसे तेज़ और स्टेबल मॉडल
        )
        
        # AI का जवाब निकालना
        bot_response = chat_completion.choices[0].message.content
        await update.message.reply_text(bot_response)
        
    except Exception as e:
        logging.error(f"Error while calling Groq API: {e}")
        await update.message.reply_text("माफ़ कीजिएगा, इस समय Groq AI से जुड़ने में कोई समस्या आ रही है।")

# 3. बॉट को चालू करने का मुख्य फंक्शन
def main():
    if not TELEGRAM_TOKEN or not GROQ_API_KEY:
        logging.critical("ERROR: TELEGRAM_TOKEN या GROQ_API_KEY सेट नहीं है! कृपया Render Environment Variables चेक करें।")
        return

    # ApplicationBuilder का उपयोग (v20+ का स्टैंडर्ड तरीका)
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # कमांड और मैसेज हैंडलर्स को जोड़ना
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # बॉट को चालू करना (यह पोलिंग मोड में हमेशा चलता रहेगा)
    print("बॉट सफलतापूर्वक शुरू हो गया है...")
    application.run_polling()

if __name__ == '__main__':
    main()
