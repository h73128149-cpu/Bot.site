import os
import json
import telebot
from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# ==================== تنظیمات اصلی ====================
TOKEN = "8844989420:AAHesRVykZ10Ra2AIvzhn7iZkwC4Kzd1bP0"
BOT_USERNAME = "Hesamm_vpnbot"

# اطلاعات حساب و مدیریت
CARD_NUMBER = "6219061837027282"
CARD_HOLDER = "عابدی"
SUPPORT_USERNAME = "Pv_HE33AM"
ADMIN_CHAT_ID = 6889501272

# لینک تصویر QR Code یا لوگو در گیتهاب
QR_IMAGE_PATH = "https://raw.githubusercontent.com/h73128149-cpu/Bot.site/main/qr.png"

# لینک مینی‌اپ روی GitHub Pages
WEB_APP_URL = "https://h73128149-cpu.github.io/mini-app/"

# راه‌اندازی ربات
bot = telebot.TeleBot(TOKEN)

# دیتابیس متغیری ساده (در حافظه)
users_set = set()
referral_counts = {}
user_phones = {}

# ==================== سرویس نگهداری ربات (Flask Keep-Alive) ====================
FLASK_APP = Flask('')

@FLASK_APP.route('/')
def home():
    return "Bot & MiniApp are active!"

def run():
    FLASK_APP.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# ==================== کیبوردهای اصلی ====================
def main_menu_markup(user_id):
    markup = InlineKeyboardMarkup(row_width=1)
    
    markup.add(
        InlineKeyboardButton("🚀 ورود به مینی‌اپ فروشگاه", web_app=WebAppInfo(url=WEB_APP_URL)),
        InlineKeyboardButton("🛒 خرید سریع از ربات", callback_data="buy_plan"),
        InlineKeyboardButton("🎁 دریافت سرور رایگان (رفرال)", callback_data="referral_menu"),
        InlineKeyboardButton("📱 برنامه‌های اتصال", callback_data="apps_menu"),
        InlineKeyboardButton("📞 پشتیبانی مستقیم", callback_data="support")
    )
    if user_id == ADMIN_CHAT_ID:
        markup.add(InlineKeyboardButton("⚙️ پنل مدیریت ربات", callback_data="admin_panel"))
    return markup

# ==================== هندلرهای دستورات ====================

# 1. دستور /start (کاملاً مستقل برای نمایش منوی اصلی)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        user_id = message.from_user.id
        user_name = message.from_user.first_name.replace("*", "").replace("_", "") if message.from_user.first_name else "کاربر"
        username = f"@{message.from_user.username}" if message.from_user.username else "ندارد"
        
        is_new_user = user_id not in users_set
        users_set.add(user_id)

        # گزارش ورود کاربر جدید به ادمین
        if is_new_user and user_id != ADMIN_CHAT_ID:
            log_text = f"👤 **کاربر جدید ربات را استارت کرد:**\n\nنام: {user_name}\nیوزرنیم: {username}\nآیدی عددی: `{user_id}`"
            try:
                bot.send_message(ADMIN_CHAT_ID, log_text, parse_mode="Markdown")
            except Exception as e:
                print(f"Error sending log to admin: {e}")

        welcome_text = (
            f"سلام {user_name} عزیز 👋\n\n"
            f"به ربات فروشگاهی **Hes_VPN** خوش آمدید!\n\n"
            f"از منوی زیر می‌توانید مینی‌اپ را باز کنید یا از دکمه‌های سریع استفاده کنید."
        )
        bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu_markup(user_id), parse_mode="Markdown")

    except Exception as e:
        print(f"Start Error: {e}")

# 2. دستور /shop (مخصوص سفارشات ارسالی از مینی‌اپ)
@bot.message_handler(commands=['shop'])
def handle_shop_command(message):
    try:
        command_args = message.text.split()
        if len(command_args) > 1:
            plan_key = command_args[1]
            plans = {
                "plan_10gb": ("۱۰ گیگابایت", "۵۰,۰۰۰ تومان"),
                "plan_20gb": ("۲۰ گیگابایت", "۱۰۰,۰۰۰ تومان"),
                "plan_30gb": ("۳۰ گیگابایت", "۱۵۰,۰۰۰ تومان"),
                "plan_unlimited": ("نامحدود (ماهانه)", "۳۵۰,۰۰۰ تومان")
            }
            plan_name, plan_price = plans.get(plan_key, ("نامشخص", "۰"))
            
            response_text = (
                f"🛒 **سفارش جدید شما از مینی‌اپ**\n\n"
                f"📌 **پلن انتخابی:** {plan_name}\n"
                f"💳 **مبلغ قابل پرداخت:** {plan_price}\n\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"💳 **شماره کارت جهت واریز:**\n"
                f"`{CARD_NUMBER}`\n"
                f"👤 **به نام:** {CARD_HOLDER}\n"
                f"━━━━━━━━━━━━━━━━━━━\n\n"
                f"📸 لطفاً پس از واریز، **تصویر فیش واریزی** خود را همین‌جا ارسال کنید."
            )
            bot.send_message(message.chat.id, response_text, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "🛒 لطفاً از طریق مینی‌اپ یا منوی اصلی اقدام به انتخاب پلن کنید.")
    except Exception as e:
        print(f"Shop Error: {e}")

# 3. دریافت داده‌های مستقیم مینی‌اپ
@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
    try:
        data = json.loads(message.web_app_data.data)
        if data.get("action") == "buy_plan":
            plan = data.get("plan")
            price = data.get("price")
            
            response_text = (
                f"🛒 **سفارش جدید از مینی‌‌اپ**\n\n"
                f"📌 **پلن انتخابی:** {plan}\n"
                f"💳 **مبلغ قابل پرداخت:** {price}\n\n"
                f"💳 **شماره کارت جهت واریز:**\n"
                f"`{CARD_NUMBER}`\n"
                f"👤 **به نام:** {CARD_HOLDER}\n\n"
                f"📸 لطفاً پس از واریز، **تصویر فیش واریزی** خود را همین‌جا ارسال کنید."
            )
            bot.send_message(message.chat.id, response_text, parse_mode="Markdown")
    except Exception as e:
        print(f"WebApp Error: {e}")

# 4. دریافت فیش واریزی (عکس)
@bot.message_handler(content_types=['photo'])
def handle_receipt(message):
    user_id = message.from_user.id
    safe_name = message.from_user.first_name.replace("*", "").replace("_", "") if message.from_user.first_name else "کاربر"
    safe_username = f"@{message.from_user.username}" if message.from_user.username else "ندارد"
    
    caption_info = (
        f"💳 **رسید واریزی جدید دریافت شد**\n\n"
        f"👤 **نام:** {safe_name}\n"
        f"🆔 **یوزرنیم:** {safe_username}\n"
        f"🔢 **آیدی عددی:** `{user_id}`\n"
    )
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("✅ تأیید و ارسال کانفیگ", callback_data=f"approve_{user_id}"),
        InlineKeyboardButton("❌ رد فیش", callback_data=f"reject_{user_id}")
    )
    
    try:
        bot.send_photo(ADMIN_CHAT_ID, message.photo[-1].file_id, caption=caption_info, reply_markup=markup, parse_mode="Markdown")
        bot.reply_to(message, "✅ رسید شما با موفقیت برای مدیریت ارسال شد. پس از بررسی، کانفیگ برای شما ارسال می‌شود.")
    except Exception as e:
        print(f"Photo error: {e}")

# 5. پاسخ به دکمه‌های شیشه‌ای
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id
    
    if call.data == "buy_plan":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("⚡ ۱۰ گیگ", callback_data="plan_10gb"),
            InlineKeyboardButton("🔥 ۲۰ گیگ", callback_data="plan_20gb"),
            InlineKeyboardButton("💎 ۳۰ گیگ", callback_data="plan_30gb"),
            InlineKeyboardButton("👑 نامحدود", callback_data="plan_unlimited"),
            InlineKeyboardButton("🔙 بازگشت", callback_data="back_home")
        )
        bot.edit_message_text("🛒 لطفاً پلن مورد نظر خود را انتخاب کنید:", chat_id=user_id, message_id=message_id, reply_markup=markup)
        
    elif call.data.startswith("plan_"):
        plans = {
            "plan_10gb": ("۱۰ گیگابایت", "۵۰,۰۰۰ تومان"),
            "plan_20gb": ("۲۰ گیگابایت", "۱۰۰,۰۰۰ تومان"),
            "plan_30gb": ("۳۰ گیگابایت", "۱۵۰,۰۰۰ تومان"),
            "plan_unlimited": ("نامحدود", "۳۵۰,۰۰۰ تومان")
        }
        plan_name, plan_price = plans.get(call.data, ("نامشخص", "0"))
        
        text = (
            f"📌 **پلن انتخابی:** {plan_name}\n"
            f"💳 **مبلغ:** {plan_price}\n\n"
            f"شماره کارت جهت واریز:\n"
            f"`{CARD_NUMBER}` ({CARD_HOLDER})\n\n"
            f"📸 لطفاً فیش واریزی را همین‌جا بفرستید."
        )
        bot.send_message(user_id, text, parse_mode="Markdown")
        bot.answer_callback_query(call.id)

    elif call.data == "back_home":
        bot.edit_message_text("به منوی اصلی بازگشتید:", chat_id=user_id, message_id=message_id, reply_markup=main_menu_markup(user_id))

# ==================== اجرای ربات ====================
if __name__ == '__main__':
    keep_alive()
    print("Bot is running...")
    bot.infinity_polling(skip_pending=True)
