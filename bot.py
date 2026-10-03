import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import random

# توکن ربات شما
TOKEN = "8844989420:AAEASNZoEecyzvIhM14VrBoTppv-ElfzJtM"

# یوزرنیم دقیق ربات شما (بدون @)
BOT_USERNAME = "Hesamm_vpnbot"

# اطلاعات مالی و پشتیبانی
CARD_NUMBER = "6219861837027282"
CARD_HOLDER = "عابدینی"
SUPPORT_USERNAME = "Pv_HE33AM"
ADMIN_CHAT_ID = 6889501272

# اطلاعات کانال پرایوت کانفیگ شما و لیست پیام‌های آن (از ۱۵ تا ۲۰)
CONFIG_CHANNEL_ID = -1004495713858
CONFIG_MESSAGE_IDS = [15, 16, 17, 18, 19, 20]

bot = telebot.TeleBot(TOKEN)

# دیتابیس‌های موقت در حافظه
users_set = set()
referral_counts = {}  
referred_users = set()  
user_phones = {} # ذخیره شماره تلفن کاربران

def main_menu_markup(user_id):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🛒 خرید اشتراک و انتخاب حجم", callback_data="buy_plan"),
        InlineKeyboardButton("🎁 دریافت سرور رایگان (رفرال)", callback_data="referral_menu"),
        InlineKeyboardButton("📱 برنامه‌های اتصال", callback_data="apps_menu"),
        InlineKeyboardButton("📞 پشتیبانی مستقیم", callback_data="support")
    )
    if user_id == ADMIN_CHAT_ID:
        markup.add(InlineKeyboardButton("⚙️ پنل مدیریت ربات (مخصوص شما)", callback_data="admin_panel"))
    return markup

# کیبورد شکرت‌گذاری شماره تلفن (Share Contact)
def request_phone_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("📱 اشتراک‌گذاری شماره تلفن من", request_contact=True))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user
    user_name = user.first_name
    username = f"@{user.username}" if user.username else "ندارد"
    user_id = user.id

    users_set.add(user_id)

    command_args = message.text.split()
    if len(command_args) > 1 and command_args[1].startswith("ref_"):
        try:
            referrer_id = int(command_args[1].replace("ref_", ""))
            if referrer_id != user_id and user_id not in referred_users:
                referred_users.add(user_id)
                referral_counts[referrer_id] = referral_counts.get(referrer_id, 0) + 1
                try:
                    bot.send_message(
                        referrer_id,
                        f"🎉 یک نفر با لینک دعوت شما وارد ربات شد!\n"
                        f"👥 تعداد زیرمجموعه‌های شما: {referral_counts[referrer_id]} نفر"
                    )
                except Exception:
                    pass
        except Exception as e:
            print(f"Referral error: {e}")

    if user_id != ADMIN_CHAT_ID:
        log_text = (
            f"🚨 یک کاربر جدید ربات را استارت زد!\n\n"
            f"👤 نام: {user_name}\n"
            f"🆔 یوزرنیم: {username}\n"
            f"🔢 آیدی عددی: {user_id}"
        )
        try:
            bot.send_message(ADMIN_CHAT_ID, log_text)
        except Exception as e:
            print(f"Error sending log to admin: {e}")

    welcome_text = (
        f"سلام {user_name} عزیز! 🌟\n"
        "به ربات فروشگاهی و مدیریت کانفیگ خوش اومدی.\n\n"
        "👇 **لطفاً برای ادامه و تایید هویت، شماره تلفن خود را از طریق دکمه‌ی زیر به اشتراک بگذارید:**"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=request_phone_markup())

# دریافت شماره تلفن ارسالی از کاربر
@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    user_id = message.from_user.id
    if message.contact is not None:
        phone_number = message.contact.phone_number
        user_phones[user_id] = phone_number
        
        # اطلاع‌رسانی به ادمین درباره شماره کاربر
        try:
            bot.send_message(
                ADMIN_CHAT_ID,
                f"📞 **شماره جدید دریافت شد!**\n"
                f"👤 کاربر: {message.from_user.first_name}\n"
                f"🆔 آیدی: `{user_id}`\n"
                f"📱 شماره: `+{phone_number}`",
                parse_mode="Markdown"
            )
        except Exception:
            pass

        bot.send_message(
            message.chat.id,
            "✅ شماره شما با موفقیت ثبت شد!\n\nاکنون می‌توانید از منوی زیر استفاده کنید:",
            reply_markup=main_menu_markup(user_id)
        )

@bot.message_handler(commands=['send'])
def broadcast_message(message):
    if message.from_user.id == ADMIN_CHAT_ID:
        text_to_send = message.text.replace("/send", "").strip()
        if not text_to_send:
            bot.reply_to(message, "⚠ لطفاً متنی که می‌خواهی ارسال کنی را بعد از دستور /send بنویس.")
            return
        
        success_count = 0
        for uid in users_set:
            try:
                bot.send_message(uid, f"📢 **پیام مدیریت:**\n\n{text_to_send}", parse_mode="Markdown")
                success_count += 1
            except Exception as e:
                print(f"Could not send to {uid}: {e}")
        
        bot.reply_to(message, f"✅ پیام با موفقیت به {success_count} کاربر ارسال شد.")
    else:
        bot.reply_to(message, "❌ شما دسترسی به این دستور را ندارید.")

@bot.message_handler(content_types=['photo'])
def handle_receipt(message):
    user = message.from_user
    
    if user.id == ADMIN_CHAT_ID:
        bot.reply_to(message, "ℹ این عکس از طرف شما (ادمین) ارسال شد.")
        return
    
    try:
        phone_info = user_phones.get(user.id, "ثبت نشده / ارسال نکرده")
        caption_info = (
            f"📥 رسید واریز جدید دریافت شد!\n\n"
            f"👤 نام: {user.first_name}\n"
            f"🆔 یوزرنیم: @{user.username if user.username else 'ندارد'}\n"
            f"🔢 آیدی عددی: {user.id}\n"
            f"📱 شماره تلفن: +{phone_info}"
        )
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("✅ تایید و ارسال کانفیگ", callback_data=f"approve_{user.id}"),
            InlineKeyboardButton("❌ رد رسید", callback_data=f"reject_{user.id}")
        )
        
        bot.send_photo(ADMIN_CHAT_ID, message.photo[-1].file_id, caption=caption_info, reply_markup=markup)
        bot.reply_to(message, "⏳ **منتظر تایید رسید باشید با تشکر 🙏**", parse_mode="Markdown")
    except Exception as e:
        print(f"Photo error: {e}")
        bot.reply_to(message, "❌ خطایی در ارسال رسید رخ داد. لطفاً تصویر را مجدد بفرستید.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = call.from_user.id

    if call.data.startswith("approve_") or call.data.startswith("reject_"):
        if user_id != ADMIN_CHAT_ID:
            bot.answer_callback_query(call.id, "❌ شما دسترسی ندارید!", show_alert=True)
            return
        
        action, target_user_id = call.data.split("_")
        target_user_id = int(target_user_id)
        
        if action == "approve":
            try:
                bot.send_message(
                    target_user_id,
                    "🎉 **پرداخت شما توسط مدیریت تایید شد!**\n"
                    "کانفیگ اختصاصی شما (انتخاب رندوم):"
                )
                
                # انتخاب تصادفی یکی از پیام‌های ۱۵ تا ۲۰ از کانال خصوصی
                random_msg_id = random.choice(CONFIG_MESSAGE_IDS)
                bot.forward_message(target_user_id, CONFIG_CHANNEL_ID, random_msg_id)
                
                bot.answer_callback_query(call.id, f"✅ رسید تایید شد و کانفیگ شماره {random_msg_id} ارسال گردید.")
                bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=message_id,
                    caption=(call.message.caption or "") + f"\n\n[✅ تایید شد و کانفیگ شماره {random_msg_id} ارسال گردید]"
                )
            except Exception as e:
                print(f"Error forwarding random config: {e}")
                bot.answer_callback_query(call.id, "⚠ خطا در ارسال کانفیگ (ربات در کانال ادمین نیست یا آیدی اشتباه است).", show_alert=True)
        
        elif action == "reject":
            try:
                bot.send_message(
                    target_user_id,
                    "❌ **متأسفانه رسید واریز شما توسط مدیریت رد شد.**\n"
                    "اگر اشتباهی رخ داده است، لطفاً با پشتیبانی در ارتباط باشید."
                )
                bot.answer_callback_query(call.id, "❌ رسید رد شد.")
                bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=message_id,
                    caption=(call.message.caption or "") + "\n\n[❌ رسید رد شد]"
                )
            except Exception as e:
                print(f"Error rejecting: {e}")
        return

    if call.data == "buy_plan":
        text = "📦 **لطفاً حجم مورد نظر خود را انتخاب کنید:**"
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("⚡ ۱۰ گیگابایت - ۵۰ ت", callback_data="plan_10gb"),
            InlineKeyboardButton("🔥 ۲۰ گیگابایت - ۱۰۰ ت", callback_data="plan_20gb"),
            InlineKeyboardButton("💎 ۳۰ گیگابایت - ۱۵۰ ت", callback_data="plan_30gb"),
            InlineKeyboardButton("👑 نامحدود ماهانه - ۳۵۰ ت", callback_data="plan_unlimited"),
            InlineKeyboardButton("« بازگشت به منوی اصلی", callback_data="back_home")
        )
        bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=markup)

    elif call.data.startswith("plan_"):
        plan_details = {
            "plan_10gb": {"name": "۱۰ گیگابایت", "price": "۵۰,۰۰۰ تومان"},
            "plan_20gb": {"name": "۲۰ گیگابایت", "price": "۱۰۰,۰۰۰ تومان"},
            "plan_30gb": {"name": "۳۰ گیگابایت", "price": "۱۵۰,۰۰۰ تومان"},
            "plan_unlimited": {"name": "حجم نامحدود (ماهانه)", "price": "۳۵۰,۰۰۰ تومان"}
        }
        
        selected = plan_details.get(call.data, {"name": "نامشخص", "price": "۰"})
        
        text = (
            f"🛒 **پلن انتخابی شما:** {selected['name']}\n"
            f"💵 **مبلغ قابل پرداخت:** {selected['price']}\n\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "💳 **شماره کارت برای واریز وجه:**\n"
            f"`{CARD_NUMBER}`\n"
            f"بنام: **{CARD_HOLDER}**\n"
            "━━━━━━━━━━━━━━━━━━━\n\n"
            "📌 **راهنمای پرداخت:**\n"
            "مبلغ فوق را به کارت بالا واریز کرده و سپس **عکس فیش واریزی** را همینجا مستقیماً برای ربات بفرستید."
        )
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("« بازگشت به لیست پلن‌ها", callback_data="buy_plan")
        )
        bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=markup)

    elif call.data == "referral_menu":
        user_referrals = referral_counts.get(user_id, 0)
        ref_link = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"
        
        text = (
            "🎁 **سیستم دعوت از دوستان (رفرال)**\n\n"
            "با دعوت از دوستانتان به ربات، جایزه بگیرید!\n"
            "📌 **قانون جایزه:** با دعوت از **۱۰ نفر**، یک **سرور نامحدود یک ماهه** رایگان هدیه بگیرید.\n\n"
            f"👥 تعداد زیرمجموعه‌های شما: `{user_referrals} / 10` نفر\n\n"
            "🔗 **لینک دعوت اختصاصی شما:**\n"
            f"`{ref_link}`\n\n"
            "👇 لینک بالا را برای دوستانتان بفرستید تا با آن وارد ربات شوند."
        )
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("« بازگشت به منوی اصلی", callback_data="back_home")
        )
        bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=markup)

    elif call.data == "admin_panel":
        if user_id != ADMIN_CHAT_ID:
            bot.answer_callback_query(call.id, "❌ شما دسترسی ندارید!", show_alert=True)
            return
        
        total_users = len(users_set)
        
        referrers_text = ""
        if referral_counts:
            for ref_id, count in referral_counts.items():
                referrers_text += f"• آیدی عددی `{ref_id}`: **{count}** زیرمجموعه\n"
        else:
            referrers_text = "هنوز کسی زیرمجموعه‌ای ثبت نکرده است.\n"

        text = (
            "⚙️ **پنل مدیریت ربات**\n\n"
            f"👥 **تعداد کل کاربران ربات:** `{total_users}` نفر\n\n"
            "📊 **آمار کاربران دارای رفرال:**\n"
            f"{referrers_text}"
        )
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("🔄 بروزرسانی آمار", callback_data="admin_panel"),
            InlineKeyboardButton("« بازگشت به منوی اصلی", callback_data="back_home")
        )
        bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=markup)

    elif call.data == "apps_menu":
        text = "📱 **برنامه‌های اتصال:**\n• NekoBox\n• v2rayNG"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("« بازگشت به منوی اصلی", callback_data="back_home"))
        bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=markup)

    elif call.data == "support":
        text = (
            "💬 **پشتیبانی و ارتباط با مدیریت:**\n\n"
            "اگر سوال، مشکل یا نیاز به راهنمایی دارید، می‌توانید از طریق دکمه زیر مستقیماً به پیوی پشتیبانی پیام دهید:"
        )
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("👨‍💻 ارتباط مستقیم با پشتیبانی (پیوی)", url=f"https://t.me/{SUPPORT_USERNAME}"),
            InlineKeyboardButton("« بازگشت به منوی اصلی", callback_data="back_home")
        )
        bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=markup)

    elif call.data == "back_home":
        user_name = call.from_user.first_name
        welcome_text = (
            f"سلام **{user_name}** عزیز! 🌟\n"
            "به ربات فروشگاهی و مدیریت کانفیگ خوش اومدی.\n\n"
            "از دکمه‌های زیر برای دسترسی به بخش‌های مختلف استفاده کن:"
        )
        bot.edit_message_text(welcome_text, chat_id, message_id, parse_mode="Markdown", reply_markup=main_menu_markup(user_id))

print("🚀 Ultimate Bot with Random Config & Phone Share is running...")
bot.infinity_polling()
