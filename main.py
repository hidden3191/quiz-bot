import os, json, re, logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from groq import Groq

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_KEY)

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Ready ✅\nUse: /quiz ssc gd")

def clean_json(text):
    m = re.search(r'\{.*\}', text, re.DOTALL)
    if m:
        text = m.group(0)
    return json.loads(text)

async def quiz(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(ctx.args) if ctx.args else "general knowledge"
    await update.message.reply_text(f"Generating: {topic}...")
    prompt = f'Return ONLY JSON: {{"q":"question under 200 chars","opts":["A <80 chars","B","C","D"],"ans":0}} Topic: {topic}'
    data = None
    try:
        resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":prompt}], temperature=0.5, max_tokens=400)
        j = clean_json(resp.choices[0].message.content)
        q = j.get("q") or j.get("question")
        opts = j.get("opts") or j.get("options")
        ans = j.get("ans",0)
        if q and opts:
            data = {"q": str(q)[:250], "opts": [str(o)[:90] for o in opts][:4], "ans": int(ans)}
    except Exception as e:
        logging.error(e)
    if not data:
        data = {"q": f"Which is correct about {topic}?", "opts": [f"{topic} Basic", f"{topic} Advanced", f"{topic} History", "None"], "ans": 0}
    await ctx.bot.send_poll(chat_id=update.effective_chat.id, question=data["q"], options=data["opts"], type="quiz", correct_option_id=data["ans"] % len(data["opts"]), is_anonymous=False)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("quiz", quiz))
app.run_polling()
