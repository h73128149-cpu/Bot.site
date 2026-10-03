import telebot
from telebot import types

# توکن ربات و آیدی عددی شما
TOKEN = '8844989420:AAHZEwmt9SdadVuzoqe-vApgBmBYzJbp7Nc'
ADMIN_ID = 670395729

bot = telebot.TeleBot(TOKEN)

# منوی اصلی ربات
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🛍 خرید اشتراک / قیمت‌ها")
    btn2 = types.KeyboardButton("💳 ارسال رسید پرداخت")
    markup.add(btn1)
    markup.add(btn2)
    return markup

# دستور /start
@bot.message_handler(commands=['start'])
def start(message):
    text = (
        f"سلام {message.from_user.first_name} عزیز! 👋\n"
        "به ربات فروش کانفیگ اختصاصی خوش آمدید.\n\n"
        "از منوی زیر جهت مشاهده قیمت‌ها یا ارسال رسید اقدام کنید:"
    )
    bot.send_message(message.chat.id, text, reply_markup=main_keyboard())

# ۱. نمایش لیست قیمت‌ها و اطلاعات پرداخت
@bot.message_handler(func=lambda message: message.text == "🛍 خرید اشتراک / قیمت‌ها")
def show_plans(message):
    plans_text = (
        "📊 **لیست پلن‌های اختصاصی V2Ray:**\n\n"
        "🔹 **۱ ماهه (۳۰ گیگ):** ۵۰,۰۰۰ تومان\n"
        "🔹 **۱ ماهه (۵۰ گیگ):** ۸۰,۰۰۰ تومان\n"
        "🔹 **۱ ماهه (نامحدود):** ۱۵۰,۰۰۰ تومان\n\n"
        "💳 **شماره کارت جهت واریز:**\n"
        "`6037-9979-0000-0000`\n"
        "👤 به نام: حسام\n\n"
        "📌 پس از واریز، عکس رسید پرداخت را همین‌جا ارسال کنید."
    )
    bot.send_message(message.chat.id, plans_text, parse_mode="Markdown")

# ۲. دکمه ارسال رسید (راهنمایی کاربر)
@bot.message_handler(func=lambda message: message.text == "💳 ارسال رسید پرداخت")
def prompt_receipt(message):
    bot.send_message(message.chat.id, "لطفاً عکس رسید پرداخت خود را همین‌جا ارسال کنید.")

# ۳. دریافت تصویر رسید از کاربر و ارسال برای ادمین
@bot.message_handler(content_types=['photo'])
def handle_receipt(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    # دکمه‌های تایید یا رد برای ادمین
    markup = types.InlineKeyboardMarkup()
    btn_approve = types.InlineKeyboardButton("✅ تایید رسید", callback_data=f"approve_{user_id}")
    btn_reject = types.InlineKeyboardButton("❌ رد رسید", callback_data=f"reject_{user_id}")
    markup.add(btn_approve, btn_reject)
    
    # ارسال عکس رسید برای ادمین
    bot.send_photo(
        ADMIN_ID, 
        message.photo[-1].file_id, 
        caption=f"📥 **رسید جدید دریافت شد!**\n\n👤 کاربر: {user_name}\n🆔 آیدی عددی: `{user_id}`",
        parse_mode="Markdown",
        reply_markup=markup
    )
    
    bot.reply_to(message, "⏳ رسید شما دریافت شد و برای ادمین ارسال گردید. به محض تایید، اشتراک برایتان فرستاده می‌شود.")

# ۴. مدیریت دکمه‌های تایید و رد توسط ادمین
@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    if call.data.startswith("approve_"):
        user_id = int(call.data.split("_")[1])
        
        caption_text = (
            "✅ **پرداخت شما با موفقیت تایید شد!**\n\n"
            "🌐 **اشتراک اختصاصی شما آماده است:**\n"
            "برای اتصال سریع، QR Code بالا را در برنامه **v2rayNG** یا **MahsaNG** اسکن کنید.\n\n"
            "🔗 **یا لینک زیر را کپی و وارد برنامه کنید:**\n"
            "`https://3a2p7kbakilve14mbb.3qaxdyijoct8hccr.workers.dev/G1MHF70jbW0koP/sub/normal?app=xray#%F0%9F%92%A6%20BPB%20Normal`\n\n"
            "⚡️ از خرید و اعتماد شما متشکریم! ❤️"
        )
        
        # ارسال همان تک عکس qr.png ثابت موجود در پروژه
        try:
            with open("qr.png", "rb") as qr_file:
                bot.send_photo(user_id, qr_file, caption=caption_text, parse_mode="Markdown")
            
            bot.answer_callback_query(call.id, "✅ رسید تایید شد و QR Code فرستاده شد.")
            bot.edit_message_caption("✅ این رسید تایید شد.", chat_id=ADMIN_ID, message_id=call.message.message_id)
        except Exception as e:
            bot.send_message(ADMIN_ID, f"❌ خطایی رخ داد (بررسی کنید فایل qr.png در کنار bot.py باشد):\n{e}")

    elif call.data.startswith("reject_"):
        user_id = int(call.data.split("_")[1])
        bot.send_message(user_id, "❌ **رسید شما تایید نشد.**\nلطفاً رسید معتبر ارسال کنید یا با پشتیبانی تماس بگیرید.")
        bot.answer_callback_query(call.id, "❌ رسید رد شد.")
        bot.edit_message_caption("❌ این رسید رد شد.", chat_id=ADMIN_ID, message_id=call.message.message_id)

bot.infinity_polling(skip_pending_requests=True)
