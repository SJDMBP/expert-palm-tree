import os
import json
import asyncio
import random
import logging
from http.server import BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# تنظیمات لاگ برای مشاهده خطاها در پنل Vercel
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# دریافت توکن از متغیرهای محیطی
TOKEN = os.getenv("BOT_TOKEN")

# بانک چالش‌های فارسی
PROMPTS = {
    "mild": [
        "یک فانتزی مخفی را در گوش شریک زندگی‌تان زمزمه کنید.",
        "به مدت ۶۰ ثانیه گردن شریکتان را ماساژ دهید.",
        "اولین باری که مرا دیدی چه حسی داشتی؟",
        "۳۰ ثانیه بدون صحبت کردن به چشمان هم خیره شوید.",
        "جذاب‌ترین ویژگی ظاهری شریکتان را توصیف کنید."
    ],
    "spicy": [
        "چشمان شریکتان را ببندید و جایی غیرمنتظره از بدنش را لمس کنید.",
        "یک تکه از لباس شریکتان را فقط با دندان‌هایتان در بیاورید.",
        "پوزیشن مورد علاقه‌تان را با حرکات دست نشان دهید.",
        "گردن شریکتان را آنقدر ببوسید تا صدایش در بیاید.",
        "مسیری از استخوان یقه تا ناف شریکتان را ببوسید."
    ],
    "flame": [
        "۲ دقیقه آینده مال شماست تا هر کاری می‌خواهید با شریکتان انجام دهید.",
        "دو تکه از لباس‌های خودتان را در بیاورید.",
        "با جزئیات دقیق توصیف کنید که بعداً می‌خواهید چه بلایی سر من بیاورید!",
        "یک بوسه فرانسوی عمیق که حداقل ۶۰ ثانیه طول بکشد داشته باشید.",
        "لباس زیر شریکتان را بدون استفاده از دست در بیاورید."
    ]
}

# ساخت اپلیکیشن ربات
app = ApplicationBuilder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر دستور استارت"""
    keyboard = [[InlineKeyboardButton("🎲 تاس ریختن و شروع", callback_data="roll")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🔥 به ربات *شب اخگرها* خوش آمدید!\n\nآماده یک شب رمانتیک و داغ هستید؟ نوبت نفر اول است...",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر کلیک روی دکمه تاس"""
    query = update.callback_query
    await query.answer()
    
    # تولید حرارت تصادفی (چون در سرورلس حافظه دائمی ساده نداریم)
    heat = random.randint(10, 100)
    
    if heat > 70: category, cat_name = "flame", "🔥 آتشین (Flame)"
    elif heat > 35: category, cat_name = "spicy", "🌶 تند (Spicy)"
    else: category, cat_name = "mild", "💖 ملایم (Mild)"
        
    prompt = random.choice(PROMPTS[category])
    
    response_text = (
        f"📊 *سطح حرارت این نوبت:* {heat}%\n"
        f"🏷 *نوع چالش:* {cat_name}\n\n"
        f"📍 *چالش شما:*\n_{prompt}_"
    )
    
    keyboard = [[InlineKeyboardButton("🎲 نوبت نفر بعدی", callback_data="roll")]]
    await query.edit_message_text(
        text=response_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# ثبت هندلرها
app.add_handler(CommandHandler('start', start))
app.add_handler(CallbackQueryHandler(handle_roll, pattern="roll"))

# کلاس هندلر برای Vercel
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        update_data = json.loads(post_data.decode('utf-8'))
        
        async def process():
            update = Update.de_json(update_data, app.bot)
            async with app:
                await app.process_update(update)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(process())
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ok')

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running...')
