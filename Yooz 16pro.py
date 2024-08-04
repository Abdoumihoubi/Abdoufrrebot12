import telebot
import requests
import shelve
from flask import Flask
from telebot import types
from threading import Thread

app = Flask('')

# توكن البوت من BotFather
TOKEN = '7450872339:AAEJXoUdcdcMqmXunfdzOzPYI3qyvsOAHbc'
bot = telebot.TeleBot(TOKEN)

# قائمة بالمستخدمين المسموح لهم باستخدام البوت
ALLOWED_USERS = [7377632744, 6853679072, 5460973447, 5052911838, 7095484110, 5078196107, 7395728648]  # ضع هنا معرفات المستخدمين المسموح لهم

# دالة للتحقق من إذن المستخدم
def is_user_allowed(user_id):
    return user_id in ALLOWED_USERS

# دالة لحفظ التوكن
def save_token(user_id, token):
    with shelve.open('tokens.db') as db:
        db[str(user_id)] = token

# دالة لاسترجاع التوكن
def get_token(user_id):
    with shelve.open('tokens.db') as db:
        return db.get(str(user_id))

# دالة بدء المحادثة
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "عـذرا عزيزي انت لا تمـلك الإذن لإستخدام البوت تواصل مـع المطـور 🧑🏻‍💻@abdoumihou2000")
        return

    markup = types.ReplyKeyboardMarkup(row_width=1)
    itembtn1 = types.KeyboardButton('✅أضغط هنا لإعادة إرسال أنت بدون رمز ✅')
    markup.add(itembtn1)
    
    bot.reply_to(message, " أرسـل رقــــمك يـوز من فضـلك 📱 أو إذ كنت محفوض فتوكن إضغط على زر فقط تتم تعبئة حسابك 💎🎀", reply_markup=markup)

# دالة لمعالجة الرقم المدخل
@bot.message_handler(func=lambda message: message.text.isdigit())
def handle_number(message):
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "عـذرا عزيزي انت لا تمـلك الإذن لإستخدام البوت تواصل مـع المطـور 🧑🏻‍💻@abdoumihou2000")
        return

    num = message.text
    bot.send_message(message.chat.id, 'يتم التحقق من رقم هاتفك سيتم إرسال رمز تحقق🔍')

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'ibiza.ooredoo.dz',
        'Connection': 'Keep-Alive',
        'User-Agent': 'okhttp/4.9.3',
    }

    data = {
        'client_id': 'ibiza-app',
        'grant_type': 'password',
        'mobile-number': num,
        'language': 'AR',
    }

    response = requests.post('https://ibiza.ooredoo.dz/auth/realms/ibiza/protocol/openid-connect/token', headers=headers, data=data)
    if 'ROOGY' in response.text:
        bot.send_message(message.chat.id, 'تم إرسال رمز تحقق قم بإرساله من فضلك📨🧾')
    else:
        bot.send_message(message.chat.id, 'حدث خطأ أثناء إرسال الرمز يرجى إعادة المحاولة بعد دقيقتين ‼️')

    bot.register_next_step_handler(message, handle_otp, num)

# دالة لمعالجة الكود المدخل
def handle_otp(message, num):
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "عـذرا عزيزي انت لا تمـلك الإذن لإستخدام البوت تواصل مـع المطـور 🧑🏻‍💻@abdoumihou2000")
        return

    otp = message.text

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'ibiza.ooredoo.dz',
        'Connection': 'Keep-Alive',
        'User-Agent': 'okhttp',
    }

    data = {
        'client_id': 'ibiza-app',
        'otp': otp,
        'grant_type': 'password',
        'mobile-number': num,
        'language': 'AR',
    }

    response = requests.post('https://ibiza.ooredoo.dz/auth/realms/ibiza/protocol/openid-connect/token', headers=headers, data=data)
    access_token = response.json().get('access_token')

    if access_token:
        bot.send_message(message.chat.id, 'تم التحقق بنجاح، يتم إرسال الانترنت.......... 🪅')
        save_token(message.from_user.id, access_token)  # حفظ التوكن
        send_internet(message, access_token)
    else:
        bot.send_message(message.chat.id, 'عذرا، هناك خطأ في التحقق من رمز تحقق، يرجى إعادة المحاولة لاحقاً ‼️')

# دالة للتحقق من حجم الانترنت
def check_internet_volume(access_token):
    url = 'https://ibiza.ooredoo.dz/api/v1/mobile-bff/users/balance'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'language': 'AR',
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers)
    volume = response.json().get('accounts', [{}])[1].get('value', 'غير متاح')
    return volume

# دالة لإرسال الانترنت
def send_internet(message, access_token):
    url = 'https://ibiza.ooredoo.dz/api/v1/mobile-bff/users/mgm/info/apply'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'language': 'AR',
        'request-id': 'ef69f4c6-2ead-4b93-95df-106ef37feefd',
        'flavour-type': 'gms',
        'Content-Type': 'application/json'
    }

    payload = {
        "mgmValue": "ABC"
    }

    # التحقق من حجم الانترنت قبل تطبيق التوكن
    initial_volume = check_internet_volume(access_token)
    bot.send_message(message.chat.id, f'⊢――――اصـبر شويا من فضلك―――――⊣\n『 حجم الأنترنت تاعك قبل ما ترسل :{initial_volume} 🪪\n┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄』\n﴿ملاحظة مهمة : يمكنك التسجيل مرة واحدة كل 2 دقائق ⌛﴾')

    for _ in range(10):
        response = requests.post(url, headers=headers, json=payload).text
        if 'Request Rejecte' not in response:
            pass
        else:
            final_volume = check_internet_volume(access_token)
            bot.send_message(message.chat.id, f'┏══════ 🎁 ═══════╗\n✯✯𝐴𝐵𝐷𝑂𝑈 𝑌𝑂𝑂𝑍 𝑉𝐼𝑃✯✯\n𓊈{final_volume} 🎉𓊉              حجم أنترنت بعد إرسال 🎊\n┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n✅صالحــــــة لمدة: 7 أيامــ  📅\n\n✅ المطور  :@abdoumihou2000🇮🇹')
            break
    else:
        bot.send_message(message.chat.id, 'عذراً، حدث خطأ أثناء إرسال الانترنت، يرجى المحاولة لاحقاً ‼️')

# بدء البوت
@app.route('/')
def home():
    return "<b>telegram @X0_XV</b>"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

@bot.message_handler(func=lambda message: message.text == '✅أضغط هنا لإعادة إرسال أنت بدون رمز ✅')
def reuse_token(message):
    token = get_token(message.from_user.id)
    if token:
        send_internet(message, token)
    else:
        bot.send_message(message.chat.id, 'رقـمك ليـس محفوض ، يرجى إرسال رقمك لإعادة التسجيل.')

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling(skip_pending=True)