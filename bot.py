import os
import json
import telebot
from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# ==================== تنظیمات اصلی ====================
TOKEN = "8844989420:AAEcwPgtMFVBDYKKZoBMqGwilUNloClD5xk"
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

def request_phone_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("📱 اشتراک‌گذاری شماره تلفن", request_contact=True))
    return markup

# ==================== هندلرهای دستورات ====================

# 1. دستور start (پشتیبانی کامل از مینی‌اپ و رفرال)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name.replace("*", "").replace("_", "") if message.from_user.first_name else "کاربر"
    username = f"@{message.from_user.username}" if message.from_user.username else "ندارد"
    
    is_new_user = user_id not in users_set
    users_set.add(user_id)
    
    command_args = message.text.split()
    
    # 🔹 هندل مستقیم خرید از مینی‌اپ
    if len(command_args) > 1 and command_args[1].startswith("plan_"):
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
        return

    # 🔹 سیستم زیرمجموعه‌گیری (Referral)
    if len(command_args) > 1 and command_args[1].startswith("ref_"):
        try:
            referrer_id = int(command_args[1].replace("ref_", ""))
            if referrer_id != user_id and is_new_user and referrer_id in users_set:
                referral_counts[referrer_id] = referral_counts.get(referrer_id, 0) + 1
                bot.send_message(
                    referrer_id,
                    f"🎉 یک کاربر با لینک دعوت شما وارد ربات شد!\n👥 تعداد زیرمجموعه‌های شما: {referral_counts[referrer_id]}"
                )
        except Exception as e:
            print(f"Referral error: {e}")

    # 🔹 گزارش ورود کاربر جدید به ادمین
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


# 2. دریافت شماره تلفن
@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    user_id = message.from_user.id
    if message.contact is not None:
        phone_number = message.contact.phone_number
        user_phones[user_id] = phone_number
        
        try:
            bot.send_message(
                ADMIN_CHAT_ID,
                f"📱 **شماره جدید دریافت شد:**\n👤 کاربر: {message.from_user.first_name}\nآیدی: `{user_id}`\nشماره: `{phone_number}`",
                parse_mode="Markdown"
            )
        except Exception:
            pass
            
        bot.send_message(
            message.chat.id,
            "اکنون می‌توانید از منوی زیر استفاده کنید:",
            reply_markup=main_menu_markup(user_id)
        )


# 3. دریافت داده‌های مینی‌اپ
@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
    try:
        data = json.loads(message.web_app_data.data)
        if data.get("action") == "buy_plan":
            plan = data.get("plan")
            price = data.get("price")
            
            response_text = (
                f"🛒 **سفارش جدید از مینی‌اپ**\n\n"
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
    phone_info = user_phones.get(user_id, "ثبت نشده")
    
    caption_info = (
        f"💳 **رسید واریزی جدید دریافت شد**\n\n"
        f"👤 **نام:** {safe_name}\n"
        f"🆔 **یوزرنیم:** {safe_username}\n"
        f"🔢 **آیدی عددی:** `{user_id}`\n"
        f"📱 **شماره:** `{phone_info}`\n\n"
        f"وضعیت رسید:"
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
        bot.reply_to(message, "❌ خطا در ارسال رسید. لطفاً مجدداً تلاش کنید.")


# 5. پاسخ ادمین به فیش‌ها و دکمه‌های اینلاین
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id
    
    if call.data.startswith("approve_") or call.data.startswith("reject_"):
        if user_id != ADMIN_CHAT_ID:
            bot.answer_callback_query(call.id, "دسترسی ندارید!", show_alert=True)
            return
            
        action, target_user_id = call.data.split("_")
        target_user_id = int(target_user_id)
        
        if action == "approve":
            success_text = "🎉 **پرداخت شما با موفقیت تأیید شد!**\n\nلطفاً چند لحظه صبر کنید..."
            bot.send_message(target_user_id, success_text, parse_mode="Markdown")
            
            qr_caption = (
                f"📌 **اشتراک اختصاصی شما**\n\n"
                f"عکس بالا را با نرم‌افزار v2rayNG اسکن کنید یا کد زیر را کپی و وارد کنید.\n\n"
                f"در صورت بروز مشکل با پشتیبانی در ارتباط باشید: @{SUPPORT_USERNAME}"
            )
            try:
                bot.send_photo(target_user_id, QR_IMAGE_PATH, caption=qr_caption)
            except Exception as e:
                print(f"Error sending QR: {e}")
                
            bot.edit_message_caption("✅ رسید تأیید شد و کانفیگ ارسال گردید.", chat_id=user_id, message_id=message_id)
            bot.answer_callback_query(call.id, "تأیید شد.")
            
        elif action == "reject":
            reject_text = f"❌ **متأسفانه رسید واریزی شما تأیید نشد.**\n\nجهت پیگیری به پشتیبانی پیام دهید: @{SUPPORT_USERNAME}"
            bot.send_message(target_user_id, reject_text, parse_mode="Markdown")
            bot.edit_message_caption("❌ رسید رد شد.", chat_id=user_id, message_id=message_id)
            bot.answer_callback_query(call.id, "رد شد.")
            
    elif call.data == "buy_plan":
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
    bot.infinity_polling()
