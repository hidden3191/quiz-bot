from google import genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler
import json, asyncio, os

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")
client = genai.Client(api_key=GEMINI_KEY)
MODELS = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-2.0-flash"]
last_topic = {}

async def start(update, context):
    await update.message.reply_text("Jai Shree Krishna! 🙏 Topic bhejo, 50 Quiz bana dunga!")

async def quiz_maker(update, context):
    topic = update.message.text
    if topic.startswith('/'): return
    if topic.lower() in ["aur bhejo","aur","more","next","50 bhejo"]:
        topic = last_topic.get(update.effective_user.id, "GK")
    else:
        last_topic[update.effective_user.id] = topic
    await update.message.reply_text(f"✅ {topic} par 50 quiz bana raha hu...")
    prompt = f"Topic '{topic}' par 50 MCQ banao. Sirf JSON: [{{\"q\":\"Q\",\"options\":[\"A\",\"B\",\"C\",\"D\"],\"correct\":0,\"explain\":\"exp\"}}]"
    for model_name in MODELS:
        try:
            res = client.models.generate_content(model=model_name, contents=prompt)
            questions = json.loads(res.text.replace("```json","").replace("```","").strip())
            for q in questions:
                await context.bot.send_poll(chat_id=update.effective_chat.id, question=q['q'][:290], options=q['options'], type='quiz', correct_option_id=int(q['correct']), explanation=q['explain'][:190], is_anonymous=False)
                await asyncio.sleep(0.7)
            return
        except Exception as e:
            print(e)
            continue

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, quiz_maker))
print("Bot Started 24x7")
app.run_polling()
