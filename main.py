import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# लॉगिंग सेटअप
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Groq क्लाइंट सेटअप
groq_client = Groq(api_key=GROQ_API_KEY)

# 1. /start कमांड
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 नमस्ते! मैं आपका एडवांस AI क्विज़ जनरेटर बॉट हूँ।\n\n"
        "क्विज़ शुरू करने के लिए बस मुझे विषय का नाम लिख कर भेजें।\n"
        "जैसे: *Science quiz bhejo*, *GK quiz*, या *Maths test*"
    )

# 2. मैसेज हैंडलर (जो सीधे शानदार क्विज़ बनाकर देगा)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text("⏳ आपके लिए बेहतरीन क्विज़ तैयार किया जा रहा है, कृपया एक सेकंड रुकें...")

    # AI को क्विज़ फॉर्मेट में उत्तर देने के लिए सख्त निर्देश
    prompt = (
        f"You are an expert quiz master. The user wants a quiz about: '{user_text}'. "
        "Generate 1 high-quality multiple choice question in Hindi language. "
        "Format it exactly like this:\n"
        "प्रश्न: [सवाल यहाँ लिखें]\n"
        "A) [विकल्प 1]\n"
        "B) [विकल्प 2]\n"
        "C) [विकल्प 3]\n"
        "D) [विकल्प 4]\n\n"
        "सही उत्तर: [केवल सही विकल्प का अक्षर और उत्तर लिखें, जैसे: A) विज्ञान]"
    )

    try:
        # सबसे नया और सबसे तेज़ स्टेबल मॉडल (gemma2-9b-it)
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gemma2-9b-it", 
            temperature=0.7,
        )
        
        quiz_response = chat_completion.choices.message.content
        await update.message.reply_text(quiz_response)
        
    except Exception as e:
        logging.error(f"Groq API Error: {e}")
        # यहाँ बॉट आपको सीधे असली एरर बताएगा ताकि छुपा न रहे कि गड़बड़ कहाँ है
        error_msg = str(e)
        if "API Key" in error_msg or "401" in error_msg:
            await update.message.reply_text("❌ एरर: आपकी Groq API Key गलत या इनवैलिड है। कृपया Railway पर सही की (Key) अपडेट करें।")
        else:
            await update.message.reply_text(f"❌ कनेक्शन एरर: {error_msg}\nकृपया जांचें कि आपका Groq अकाउंट एक्टिव है या नहीं।")

def main():
    if not TELEGRAM_TOKEN or not GROQ_API_KEY:
        logging.critical("टोकन मिसिंग हैं!")
        return

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("बॉट सफलता से रन हो रहा है...")
    application.run_polling()

if __name__ == '__main__':
    main()
