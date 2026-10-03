import telebot
from telebot import types

# اطلاعات ربات و ادمین
TOKEN = '8844989420:AAHZEwmt9SdadVuzoqe-vApgBmBYzJbp7Nc'
ADMIN_ID = 670395729

bot = telebot.TeleBot(TOKEN)

# لینک سابسکریپشن اختصاصی
SUB_LINK = "https://3a2p7kbakilve14mbb.3qaxdyijoct8hccr.workers.dev/G1MHF70jbW0koP/sub/normal?app=xray#%F0%9F%92%A6%20BPB%20Normal"

# ----------------- کیبوردها -----------------

def main_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🛍 خرید اشتراک و انتخاب حجم")
    btn2 = types.KeyboardButton("🎁 دریافت سرور رایگان (رفرال)")
    btn3 = types.KeyboardButton("📱 برنامه‌های اتصال")
    btn4 = types.KeyboardButton("🤳 پشتیبانی مستقیم")
    
    markup.add(btn1)
    markup.add(btn2, btn3)
    markup.add(btn4)
    
    # منوی پنل مدیریت مخصوص ادمین
    if user_id == ADMIN_ID:
        markup.add(types.KeyboardButton("⚙️ پنل مدیریت ربات (مخصوص شما)"))
        
    return markup

# ----------------- دستور /start -----------------

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    welcome_text = (
        f"سلام {message.from_user.first_name} عزیز! 🌟\n"
        "به ربات فروشگاه و مدیریت کانفیگ خوش آمدید.\n\n"
        "لطفاً از منوی زیر بخش مورد نظر خود را انتخاب کنید:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_keyboard(user_id))

# ----------------- مدیریت دکمه‌های منو -----------------

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    text = message.text

    if text == "🛍 خرید اشتراک و انتخاب حجم":
        plans_text = (
            "📊 **لیست پلن‌ها و قیمت‌های اشتراک:**\n\n"
            "🔹 **۱ ماهه (۳۰ گیگ):** ۵۰,۰۰۰ تومان\n"
            "🔹 **۱ ماهه (۵۰ گیگ):** ۸۰,۰۰۰ تومان\n"
            "🔹 **۱ ماهه (نامحدود):** ۱۵۰,۰۰۰ تومان\n\n"
            "💳 **شماره کارت جهت واریز:**\n"
            "`6037-9979-0000-0000`\n"
            "👤 به نام: حسام\n\n"
            "📌 **راهنما:** پس از واریز، عکس رسید پرداخت خود را همین‌جا در ربات ارسال کنید تا پس از تایید، کانفیگ برایتان ارسال شود."
        )
        bot.send_message(message.chat.id, plans_text, parse_mode="Markdown")

    elif text == "🎁 دریافت سرور رایگان (رفرال)":
        referral_text = (
            "🎉 **سیستم دعوت از دوستان (رفرال)**\n\n"
            "با دعوت هر یک از دوستان خود به ربات، حجم رایگان هدیه بگیرید!\n\n"
            f"🔗 لینک اختصاصی شما:\n`https://t.me/Hes_vpn_bot?start={user_id}`"
        )
        bot.send_message(message.chat.id, referral_text, parse_mode="Markdown")

    elif text == "📱 برنامه‌های اتصال":
        apps_text = (
            "📱 **دانلود برنامه‌های مورد نیاز جهت اتصال:**\n\n"
            "🤖 **اندروید:** v2rayNG / MahsaNG\n"
            "🍎 **آیفون (iOS):** V2Box / Streisand / Shadowrocket\n"
            "💻 **ویندوز:** v2rayN / Nekoray"
        )
        bot.send_message(message.chat.id, apps_text)

    elif text == "🤳 پشتیبانی مستقیم":
        bot.send_message(message.chat.id, "جهت ارتباط با پشتیبانی به آیدی زیر پیام دهید:\n🆔 @YourAdminID")

    elif text == "⚙️ پنل مدیریت ربات (مخصوص شما)" and user_id == ADMIN_ID:
        admin_panel_text = (
            "⚙️ **پنل مدیریت ربات**\n\n"
            "👤 آیدی ادمین: `670395729`\n"
            "📊 وضعیت ربات: آنلاین و فعال 🚀"
        )
        bot.send_message(message.chat.id, admin_panel_text, parse_mode="Markdown")

# ----------------- دریافت رسید و ارسال به ادمین -----------------

@bot.message_handler(content_types=['photo'])
def handle_receipt(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    markup = types.InlineKeyboardMarkup()
    btn_approve = types.InlineKeyboardButton("✅ تایید رسید", callback_data=f"approve_{user_id}")
    btn_reject = types.InlineKeyboardButton("❌ رد رسید", callback_data=f"reject_{user_id}")
    markup.add(btn_approve, btn_reject)
    
    bot.send_photo(
        ADMIN_ID, 
        message.photo[-1].file_id, 
        caption=f"📥 **رسید جدید دریافت شد!**\n\n👤 کاربر: {user_name}\n🆔 آیدی عددی: `{user_id}`",
        parse_mode="Markdown",
        reply_markup=markup
    )
    
    bot.reply_to(message, "⏳ رسید شما دریافت شد و برای ادمین ارسال گردید. به محض تایید، اشتراک برایتان فرستاده می‌شود.")

# ----------------- تایید یا رد رسید توسط ادمین -----------------

@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    if call.data.startswith("approve_"):
        user_id = int(call.data.split("_")[1])
        
        caption_text = (
            "✅ **پرداخت شما با موفقیت تایید شد!**\n\n"
            "🌐 **اشتراک اختصاصی شما آماده است:**\n"
            "برای اتصال سریع، QR Code بالا را در برنامه اسکن کنید.\n\n"
            "🔗 **یا لینک زیر را کپی و وارد برنامه کنید:**\n"
            f"`{SUB_LINK}`\n\n"
            "⚡️ از خرید و اعتماد شما متشکریم! ❤️"
        )
        
        try:
            with open("qr.png", "rb") as qr_file:
                bot.send_photo(user_id, qr_file, caption=caption_text, parse_mode="Markdown")
            
            bot.answer_callback_query(call.id, "✅ رسید تایید شد و QR Code ارسال گردید.")
            bot.edit_message_caption("✅ این رسید تایید شد.", chat_id=ADMIN_ID, message_id=call.message.message_id)
        except Exception as e:
            bot.send_message(ADMIN_ID, f"❌ خطایی رخ داد (مطمئن شوید فایل qr.png کنار bot.py است):\n{e}")

    elif call.data.startswith("reject_"):
        user_id = int(call.data.split("_")[1])
        bot.send_message(user_id, "❌ **رسید شما تایید نشد.**\nلطفاً رسید معتبر ارسال کنید یا با پشتیبانی تماس بگیرید.")
        bot.answer_callback_query(call.id, "❌ رسید رد شد.")
        bot.edit_message_caption("❌ این رسید رد شد.", chat_id=ADMIN_ID, message_id=call.message.message_id)

# ----------------- اجرای ربات -----------------
bot.infinity_polling()
