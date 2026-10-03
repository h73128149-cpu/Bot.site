import os
import random
from threading import Thread
import telebot
from flask import Flask
from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

# ==================== تنظیمات FLASK برای زنده نگه داشتن ربات ====================
app = Flask('')


@app.route('/')
def home():
    return "Bot is active!"


def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))


def keep_alive():
    t = Thread(target=run)
    t.start()


# اجرای سرور وب قبل از استارت ربات
keep_alive()

# ==================== تنظیمات ربات ====================
TOKEN = "8844989420:AAHZEwmt9SdadVuzoqe-vApgBmBYzJbp7Nc"
BOT_USERNAME = "Hesamm_vpnbot"

CARD_NUMBER = "6219861837027282"
CARD_HOLDER = "عابدینی"
SUPPORT_USERNAME = "Pv_HE33AM"
ADMIN_CHAT_ID = 6889501272

# ✅ آدرس فایل QR Code (لینک مستقیم به عکس)
# اگر توی گیت‌هاب آپلود کردی، لینک Raw رو بذار (مثل: https://raw.githubusercontent.com/username/repo/main/qr.png)
# اگر توی سرور PythonAnywhere آپلود کردی، آدرس کامل رو بذار (مثل: http://HE33AM.pythonanywhere.com/static/qr.png)
QR_IMAGE_PATH = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/qr.png"

bot = telebot.TeleBot(TOKEN)

# دیتابیس‌های موقت در حافظه
users_set = set()
referral_counts = {}
referred_users = set()
user_phones = {}  # ذخیره شماره تلفن کاربران


# کیبورد منوی اصلی
def main_menu_markup(user_id):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(
            "🛒 خرید اشتراک و انتخاب حجم", callback_data="buy_plan"
        ),
        InlineKeyboardButton(
            "🎁 دریافت سرور رایگان (رفرال)", callback_data="referral_menu"
        ),
        InlineKeyboardButton(
            "📱 برنامه‌های اتصال", callback_data="apps_menu"
        ),
        InlineKeyboardButton(
            "📞 پشتیبانی مستقیم", callback_data="support"
        ),
    )
    if user_id == ADMIN_CHAT_ID:
        markup.add(
            InlineKeyboardButton(
                "⚙️ پنل مدیریت ربات (مخصوص شما)", callback_data="admin_panel"
            )
        )
    return markup


# کیبورد اشتراک‌گذاری شماره تلفن
def request_phone_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(
        KeyboardButton(
            "📱 اشتراک‌‌گذاری شماره تلفن من", request_contact=True
        )
    )
    return markup


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user
    user_name = user.first_name
    username = f"@{user.username}" if user.username else "ندارد"
    user_id = user.id

    is_new_user = user_id not in users_set
    users_set.add(user_id)

    # پردازش سیستم رفرال
    command_args = message.text.split()
    if len(command_args) > 1 and command_args[1].startswith("ref_"):
        try:
            referrer_id = int(command_args[1].replace("ref_", ""))
            if referrer_id != user_id and user_id not in referred_users:
                referred_users.add(user_id)
                referral_counts[referrer_id] = (
                    referral_counts.get(referrer_id, 0) + 1
                )
                try:
                    bot.send_message(
                        referrer_id,
                        f"🎉 یک نفر با لینک دعوت شما وارد ربات شد!\n"
                        f"👥 تعداد زیرمجموعه‌های شما: {referral_counts[referrer_id]} نفر",
                    )
                except Exception:
                    pass
        except Exception as e:
            print(f"Referral error: {e}")

    # ارسال گزارش ورود کاربر جدید به ادمین
    if is_new_user and user_id != ADMIN_CHAT_ID:
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

    # بررسی ثبت شدن شماره تلفن کاربر
    if user_id in user_phones:
        welcome_text = (
            f"سلام {user_name} عزیز! 🌟\n"
            "به ربات خوش آمدید.\n\n"
            "از منوی زیر بخش مورد نظر خود را انتخاب کنید:"
        )
        bot.send_message(
            message.chat.id,
            welcome_text,
            reply_markup=main_menu_markup(user_id),
        )
    else:
        welcome_text = (
            f"سلام {user_name} عزیز! 🌟\n"
            "به ربات فروشگاهی و مدیریت کانفیگ خوش اومدی.\n\n"
            "👇 **لطفاً برای ادامه و تایید هویت، شماره تلفن خود را از طریق دکمه‌ی زیر به اشتراک بگذارید:**"
        )
        bot.send_message(
            message.chat.id, welcome_text, reply_markup=request_phone_markup()
        )


@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    user_id = message.from_user.id
    if message.contact is not None:
        phone_number = message.contact.phone_number
        user_phones[user_id] = phone_number

        try:
            bot.send_message(
                ADMIN_CHAT_ID,
                f"📞 **شماره جدید دریافت شد!**\n"
                f"👤 کاربر: {message.from_user.first_name}\n"
                f"🆔 آیدی: `{user_id}`\n"
                f"📱 شماره: `+{phone_number}`",
                parse_mode="Markdown",
            )
        except Exception:
            pass

        bot.send_message(
            message.chat.id,
            "✅ شماره شما با موفقیت ثبت شد!\n\nاکنون می‌توانید از منوی زیر استفاده کنید:",
            reply_markup=main_menu_markup(user_id),
        )


@bot.message_handler(commands=['send'])
def broadcast_message(message):
    if message.from_user.id == ADMIN_CHAT_ID:
        text_to_send = message.text.replace("/send", "").strip()
        if not text_to_send:
            bot.reply_to(
                message,
                "⚠ لطفاً متنی که می‌خواهی ارسال کنی را بعد از دستور /send بنویس.",
            )
            return

        success_count = 0
        for uid in users_set:
            try:
                bot.send_message(
                    uid,
                    f"📢 **پیام مدیریت:**\n\n{text_to_send}",
                    parse_mode="Markdown",
                )
                success_count += 1
            except Exception as e:
                print(f"Could not send to {uid}: {e}")

        bot.reply_to(
            message, f"✅ پیام با موفقیت به {success_count} کاربر ارسال شد."
        )
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
            f"📥 **رسید واریز جدید دریافت شد!**\n\n"
            f"👤 نام: {user.first_name}\n"
            f"🆔 یوزرنیم: @{user.username if user.username else 'ندارد'}\n"
            f"🔢 آیدی عددی: {user.id}\n"
            f"📱 شماره تلفن: +{phone_info}\n\n"
            f"👇 لطفاً وضعیت این رسید را مشخص کنید:"
        )

        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(
                "✅ تایید و ارسال کانفیگ", callback_data=f"approve_{user.id}"
            ),
            InlineKeyboardButton(
                "❌ رد رسید", callback_data=f"reject_{user.id}"
            ),
        )

        bot.send_photo(
            ADMIN_CHAT_ID,
            message.photo[-1].file_id,
            caption=caption_info,
            parse_mode="Markdown",
            reply_markup=markup,
        )
        bot.reply_to(
            message,
            "⏳ **رسید شما با موفقیت دریافت شد.**\n"
            "لطفاً منتظر تایید مدیریت باشید. (حداکثر ۱۵ دقیقه)\n"
            "با تشکر از صبوری شما 🙏",
            parse_mode="Markdown",
        )
    except Exception as e:
        print(f"Photo error: {e}")
        bot.reply_to(
            message,
            "❌ خطایی در ارسال رسید رخ داد. لطفاً تصویر را مجدد بفرستید.",
        )


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = call.from_user.id

    if call.data.startswith("approve_") or call.data.startswith("reject_"):
        if user_id != ADMIN_CHAT_ID:
            bot.answer_callback_query(
                call.id, "❌ شما دسترسی ندارید!", show_alert=True
            )
            return

        action, target_user_id = call.data.split("_")
        target_user_id = int(target_user_id)

        if action == "approve":
            try:
                # ✅ متن ارسالی به کاربر پس از تایید ادمین
                success_text = (
                    "🎉 **پرداخت شما با موفقیت تایید شد!**\n\n"
                    "🔹 **کانفیگ اختصاصی شما به صورت QR Code در پیام بعدی ارسال می‌شود.**\n"
                    "لطفاً چند لحظه صبر کنید...\n\n"
                    "⚠️ **نکته مهم:** این کانفیگ مخصوص شماست و به هیچ عنوان آن را در اختیار دیگران قرار ندهید.\n"
                    "🌐 **برای اتصال، از برنامه‌های موجود در منوی ربات استفاده کنید.**\n\n"
                    "از خرید شما سپاسگزاریم ❤️"
                )
                bot.send_message(target_user_id, success_text, parse_mode="Markdown")

                # ✅ ارسال عکس QR Code برای کاربر
                qr_caption = (
                    "📸 **QR Code کانفیگ اختصاصی شما**\n\n"
                    "🔹 **روش استفاده:**\n"
                    "۱. عکس بالا را ذخیره کنید.\n"
                    "۲. وارد برنامه اتصال (مثل v2rayNG یا NekoBox) شوید.\n"
                    "۳. گزینه «اسکن QR Code از گالری» را انتخاب کنید.\n"
                    "۴. عکس ذخیره شده را انتخاب کنید تا کانفیگ به برنامه اضافه شود.\n\n"
                    "⚠️ **این QR Code فقط برای شماست.**"
                )
                
                # ارسال عکس از لینک
                bot.send_photo(
                    target_user_id,
                    QR_IMAGE_PATH,
                    caption=qr_caption,
                    parse_mode="Markdown"
                )

                # ✅ پیام نهایی برای کاربر بعد از ارسال کانفیگ
                final_text = (
                    "✅ **کانفیگ شما با موفقیت ارسال شد.**\n\n"
                    "🔹 **لطفاً طبق راهنمای بالا عمل کنید.**\n"
                    "🔹 در صورت بروز هرگونه مشکل، از منوی ربات با پشتیبانی در ارتباط باشید.\n\n"
                    "🌹 **روز خوبی داشته باشید!**"
                )
                bot.send_message(target_user_id, final_text, parse_mode="Markdown")

                # پاسخ به ادمین
                bot.answer_callback_query(
                    call.id,
                    f"✅ رسید تایید شد و QR Code با موفقیت ارسال گردید.",
                )
                
                # ویرایش کپشن عکس برای ادمین
                new_caption = (
                    (call.message.caption or "")
                    + f"\n\n✅ **وضعیت:** تایید شد (QR Code ارسال گردید)."
                )
                bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=message_id,
                    caption=new_caption,
                    parse_mode="Markdown",
                )
            except Exception as e:
                print(f"Error sending QR code: {e}")
                bot.answer_callback_query(
                    call.id,
                    "⚠ خطا در ارسال QR Code. لطفاً آدرس عکس را چک کنید.",
                    show_alert=True,
                )

        elif action == "reject":
            try:
                # ✅ متن ارسالی به کاربر پس از رد رسید
                reject_text = (
                    "❌ **متأسفانه رسید واریز شما توسط مدیریت تایید نشد.**\n\n"
                    "🔹 **دلایل احتمالی:**\n"
                    "• مبلغ واریزی با پلن انتخابی مطابقت ندارد.\n"
                    "• تصویر فیش واریزی ناخوانا یا نامعتبر است.\n"
                    "• واریز به حساب اشتباه انجام شده است.\n\n"
                    "💬 **در صورت اطمینان از صحت واریز، لطفاً با پشتیبانی در ارتباط باشید:**\n"
                    f"👉 @{SUPPORT_USERNAME}"
                )
                bot.send_message(target_user_id, reject_text, parse_mode="Markdown")
                
                bot.answer_callback_query(call.id, "❌ رسید رد شد.")
                
                # ویرایش کپشن عکس برای ادمین
                new_caption = (
                    (call.message.caption or "")
                    + "\n\n❌ **وضعیت:** رسید رد شد."
                )
                bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=message_id,
                    caption=new_caption,
                    parse_mode="Markdown",
                )
            except Exception as e:
                print(f"Error rejecting: {e}")
        return

    if call.data == "buy_plan":
        text = "📦 **لطفاً حجم مورد نظر خود را انتخاب کنید:**"
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(
                "⚡ ۱۰ گیگابایت - ۵۰ ت", callback_data="plan_10gb"
            ),
            InlineKeyboardButton(
                "🔥 ۲۰ گیگابایت - ۱۰۰ ت", callback_data="plan_20gb"
            ),
            InlineKeyboardButton(
                "💎 ۳۰ گیگابایت - ۱۵۰ ت", callback_data="plan_30gb"
            ),
            InlineKeyboardButton(
                "👑 نامحدود ماهانه - ۳۵۰ ت", callback_data="plan_unlimited"
            ),
            InlineKeyboardButton(
                "« بازگشت به منوی اصلی", callback_data="back_home"
            ),
        )
        bot.edit_message_text(
            text, chat_id, message_id, parse_mode="Markdown", reply_markup=markup
        )

    elif call.data.startswith("plan_"):
        plan_details = {
            "plan_10gb": {"name": "۱۰ گیگابایت", "price": "۵۰,۰۰۰ تومان"},
            "plan_20gb": {"name": "۲۰ گیگابایت", "price": "۱۰۰,۰۰۰ تومان"},
            "plan_30gb": {"name": "۳۰ گیگابایت", "price": "۱۵۰,۰۰۰ تومان"},
            "plan_unlimited": {
                "name": "حجم نامحدود (ماهانه)",
                "price": "۳۵۰,۰۰۰ تومان",
            },
        }

        selected = plan_details.get(
            call.data, {"name": "نامشخص", "price": "۰"}
        )

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
            InlineKeyboardButton(
                "« بازگشت به لیست پلن‌ها", callback_data="buy_plan"
            )
        )
        bot.edit_message_text(
            text, chat_id, message_id, parse_mode="Markdown", reply_markup=markup
        )

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
            InlineKeyboardButton(
                "« بازگشت به منوی اصلی", callback_data="back_home"
            )
        )
        bot.edit_message_text(
            text, chat_id, message_id, parse_mode="Markdown", reply_markup=markup
        )

    elif call.data == "admin_panel":
        if user_id != ADMIN_CHAT_ID:
            bot.answer_callback_query(
                call.id, "❌ شما دسترسی ندارید!", show_alert=True
            )
            return

        total_users = len(users_set)

        referrers_text = ""
        if referral_counts:
            for ref_id, count in referral_counts.items():
                referrers_text += (
                    f"• آیدی عددی `{ref_id}`: **{count}** زیرمجموعه\n"
                )
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
            InlineKeyboardButton(
                "🔄 بروزرسانی آمار", callback_data="admin_panel"
            ),
            InlineKeyboardButton(
                "« بازگشت به منوی اصلی", callback_data="back_home"
            ),
        )
        bot.edit_message_text(
            text, chat_id, message_id, parse_mode="Markdown", reply_markup=markup
        )

    elif call.data == "apps_menu":
        text = "📱 **برنامه‌های اتصال:**\n• NekoBox\n• v2rayNG"
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton(
                "« بازگشت به منوی اصلی", callback_data="back_home"
            )
        )
        bot.edit_message_text(
            text, chat_id, message_id, parse_mode="Markdown", reply_markup=markup
        )

    elif call.data == "support":
        text = (
            "💬 **پشتیبانی و ارتباط با مدیریت:**\n\n"
            "اگر سوال، مشکل یا نیاز به راهنمایی دارید، می‌توانید از طریق دکمه زیر مستقیماً به پیوی پشتیبانی پیام دهید:"
        )
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(
                "👨‍💻 ارتباط مستقیم با پشتیبانی (پیوی)",
                url=f"https://t.me/{SUPPORT_USERNAME}",
            ),
            InlineKeyboardButton(
                "« بازگشت به منوی اصلی", callback_data="back_home"
            ),
        )
        bot.edit_message_text(
            text, chat_id, message_id, parse_mode="Markdown", reply_markup=markup
        )

    elif call.data == "back_home":
        user_name = call.from_user.first_name
        welcome_text = (
            f"سلام **{user_name}** عزیز! 🌟\n"
            "به ربات فروشگاهی و مدیریت کانفیگ خوش اومدی.\n\n"
            "از دکمه‌های زیر برای دسترسی به بخش‌های مختلف استفاده کن:"
        )
        bot.edit_message_text(
            welcome_text,
            chat_id,
            message_id,
            parse_mode="Markdown",
            reply_markup=main_menu_markup(user_id),
        )


print("🚀 Ultimate Bot with QR Code is running...")
bot.infinity_polling()