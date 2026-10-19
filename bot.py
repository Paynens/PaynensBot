import telebot
from telebot import types
import time
import sqlite3

# --- TOKENS ---
MAIN_TOKEN = "8662331359:AAEYCoXS3Wh97k7A8oYZNvGKBaq-ZCBHR1Q"
ADMIN_BOT_TOKEN = "8900760892:AAHy1Kt3RQlKS5qXJavzhgj66ZxdurJcJOw"
MY_ID = "8487366702"

bot = telebot.TeleBot(MAIN_TOKEN)
admin_bot = telebot.TeleBot(ADMIN_BOT_TOKEN)

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id TEXT PRIMARY KEY, name TEXT, balance REAL, tasks_count INTEGER, 
                  referrals INTEGER, last_task_time REAL, lang TEXT)''')
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def update_db(query, params):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()
    conn.close()

init_db()

# --- LINKS ---
LINKS = [
    "https://youtu.be/TwV_gcOXQ6w?si=lFzSfz6yQxXncDah",
    "https://youtu.be/ljXFIqjLBw8?si=seH1bBoRxlkCZml0", 
    "https://youtu.be/F0OkwXKcPSE?si=ABE4IlM62yP6v7R6", "", "", "", "", "", "", "", "", "", "", ""
]

# --- KEYBOARDS ---
def main_kb(lang):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if lang == 'ar':
        kb.add("💰 اكسب المال")
        kb.add("🏦 سحب الأرباح")
        kb.row("👥 دعوة الأصدقاء", "📽 لإعلاناتكم")
        kb.row("👤 الملف الشخصي", "📊 الإحصائيات")
    else:
        kb.add("💰Earn Money")
        kb.add("🏦 Withdraw Profits")
        kb.row("👥 Invite Friends", "📽 Advertise")
        kb.row("👤 Profile", "📊 Statistics")
    return kb

def back_kb(lang):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🔙 العودة للقائمة الرئيسية" if lang == 'ar' else "🔙 Back to Main Menu")
    return kb

# --- BOT ENGINE ---
@bot.message_handler(commands=['start'])
def start(m):
    uid = str(m.chat.id)
    ref = m.text.split()[1] if len(m.text.split()) > 1 else None
    if not get_user(uid):
        conn = sqlite3.connect('bot_database.db')
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?, ?, ?, ?)", (uid, m.from_user.first_name, 0.0, 0, 0, 0.0, 'none'))
        if ref and ref != uid:
            c.execute("UPDATE users SET balance = balance + 0.5, referrals = referrals + 1 WHERE user_id=?", (ref,))
            try: admin_bot.send_message(ref, "🎁 New Referral! +0.5$")
            except: pass
        conn.commit(); conn.close()
    
    ikb = types.InlineKeyboardMarkup()
    ikb.add(types.InlineKeyboardButton("العربية 🇸🇦", callback_data="l_ar"),
            types.InlineKeyboardButton("English 🇺🇸", callback_data="l_en"))
    bot.send_message(uid, "Choose Language / اختر اللغة:", reply_markup=ikb)

@bot.callback_query_handler(func=lambda call: call.data.startswith('l_'))
def set_l(call):
    lang = call.data.split('_')[1]
    update_db("UPDATE users SET lang = ? WHERE user_id = ?", (lang, str(call.message.chat.id)))
    msg = "تم تفعيل اللغة العربية 🇸🇦" if lang == 'ar' else "English Language Activated 🇺🇸"
    bot.send_message(call.message.chat.id, msg, reply_markup=main_kb(lang))

@bot.message_handler(func=lambda m: True)
def engine(m):
    u = get_user(str(m.chat.id))
    if not u or u[6] == 'none': return
    uid, lang, txt = str(m.chat.id), u[6], m.text

    if txt in ["🔙 العودة للقائمة الرئيسية", "🔙 Back to Main Menu"]:
        bot.send_message(uid, "🏠 القائمة الرئيسية" if lang == 'ar' else "Main Menu", reply_markup=main_kb(lang))

    elif txt in ["💰 اكسب المال", "💰 Earn Money"]:
        update_db("UPDATE users SET last_task_time = ? WHERE user_id = ?", (time.time(), uid))
        task_id = u[3] + 1
        link = LINKS[u[3] % len(LINKS)]
        if lang == 'ar':
            msg = f"لإتمام المهمة {task_id} يرجى زيارة الرابط و البقاء فيه لمدة 25 ثانية لكسب 0.1$ 💸🎯."
            b1, b2 = "إضغط هنا لكسب 0.1$", "➡️ المهمة التالية"
        else:
            msg = f"To complete task {task_id}, please visit the link and stay for 25 seconds to earn 0.1$ 💸🎯."
            b1, b2 = "Click here to earn 0.1$", "➡️ Next Task"
        
        ikb = types.InlineKeyboardMarkup(row_width=1)
        ikb.add(types.InlineKeyboardButton(b1, url=link), types.InlineKeyboardButton(b2, callback_data="check_t"))
        bot.send_message(uid, msg, reply_markup=ikb)

    elif txt in ["👤 الملف الشخصي", "👤 Profile"]:
        if lang == 'ar':
            msg = f"ملفك الشخصي 🧔\n\nالاسم : {u[1]}\nالرصيد 💵 : {u[2]:.2f} USD\nعدد المهام المنفذة : {u[3]}\nالأصدقاء المدعوون: {u[4]}"
        else:
            msg = f"Your Profile 🧔\n\nName: {u[1]}\nBalance 💵: {u[2]:.2f} USD\nCompleted Tasks: {u[3]}\nInvited Friends: {u[4]}"
        bot.send_message(uid, msg)

    elif txt in ["👥 دعوة الأصدقاء", "👥 Invite Friends"]:
        link = f"https://t.me/Paynens_Bot?start={uid}"
        if lang == 'ar':
            msg = f"احصل على مكافآت بدعوة أصدقائك 👨‍👩‍👧‍👦🎁\nأرسل رابطًا إلى الأصدقاء 🖇📩\n{link}\n\nلكل صديق تمت دعوته ستربح أنت 0.5$ 💸🎊\n\nلقد دعوت: {u[4]} شخصًا 👤."
        else:
            msg = f"Get rewards by inviting your friends 👨‍👩‍👧‍👦🎁\nSend link to friends 🖇📩\n{link}\n\nFor each friend invited, you will earn 0.5$ 💸🎊\n\nYou invited: {u[4]} people 👤."
        bot.send_message(uid, msg)

    elif txt in ["📽 لإعلاناتكم", "📽 Advertise"]:
        if lang == 'ar':
            msg = ("هل لديك صفحة أو أي نشاط على منصات التواصل الإجتماعي لكن ليس لديك متابعين؟ \n \n"
                   "أنت فالمكان الصحيح 📢\n🤖 لأن البوت سيوفر لك متابعين حقيقيين و مشاهدات و زيارات حقيقية و ذالك من طريقة عملنا 👷🏻‍♂️: \n"
                   "لدينا العديد من الأشخاص حول العالم يربحون مبالغ مالية يوميا فقط من مشاهداتهم للإعلانات و الإشتراك في صفحات المعلنين 🌏💸\n\n"
                   "عروضنا للزيارات و المشاهدات: \n"
                   "🎯 ألف زيارة / مشاهدة = 2.5$ 🔎💸\n"
                   "🎯 5 ألاف زيارة / مشاهدة = 5$ 🔎💸\n"
                   "🎯 10 ألاف زيارة / مشاهدة = 7.5$ 🔎💸\n\n"
                   "📍لا تتردد فالتواصل مع الأدمن لطلب العرض اللذي تريد..! \nللتواصل مع الأدمن: @oualide_dev")
        else:
            msg = ("Do you have a page or any activity on social media platforms but don't have followers?\n\n"
                   "You are in the right place 📢\n🤖 Because the bot will provide you with real followers, views, and visits through our working method 👷🏻‍♂️:\n\n"
                   "Our offers for visits and views:\n"
                   "🎯 1,000 visits/views = 2.5$ 🔎💸\n"
                   "🎯 5,000 visits/views = 5$ 🔎💸\n\n"
                   "📍 Don't hesitate to contact the admin to request the offer you want..!\nContact Admin: @oualide_dev")
        bot.send_message(uid, msg, reply_markup=back_kb(lang))

    elif txt in ["📊 الإحصائيات", "📊 Statistics"]:
        if lang == 'ar':
            msg = "إحصائيات البوت 📊\n\nالمستخدمون في البوت 👥: 1000\nالمبلغ المكتسب من قبل المستخدمين 💰: 500 USD\nالعدد الإجمالي للزيارات و المشاهدات 🎯 : 5000"
        else:
            msg = "Bot Statistics 📊\n\nUsers in Bot 👥: 1000\nTotal Earned by Users 💰: 500 USD\nTotal Visits and Views 🎯: 5000"
        bot.send_message(uid, msg)

    elif txt in ["🏦 سحب الأرباح", "🏦 Withdraw Profits"]:
        if lang == 'ar':
            msg_pay = f"💰 الرصيد: {u[2]:.2f} USD\n\nاختر طريقة الدفع ⬇️"
        else:
            msg_pay = f"💰 Balance: {u[2]:.2f} USD\n\nChoose payment method ⬇️"
        ikb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("USDT", callback_data="w_u"))
        bot.send_message(uid, msg_pay, reply_markup=ikb)

@bot.callback_query_handler(func=lambda call: call.data == "check_t")
def check_t(call):
    uid = str(call.message.chat.id); u = get_user(uid)
    if time.time() - u[5] >= 25:
        update_db("UPDATE users SET balance = balance + 0.1, tasks_count = tasks_count + 1 WHERE user_id = ?", (uid,))
        bot.answer_callback_query(call.id, "✅ +0.1$")
        u = get_user(uid)
        task_id = u[3] + 1
        link = LINKS[u[3] % len(LINKS)]
        if u[6] == 'ar':
            msg = f"لإتمام المهمة {task_id} يرجى زيارة الرابط و البقاء فيه لمدة 25 ثانية لكسب 0.1$ 💸🎯."
            b1, b2 = "إضغط هنا لكسب 0.1$", "➡️ المهمة التالية"
        else:
            msg = f"To complete task {task_id}, please visit the link and stay for 25 seconds to earn 0.1$ 💸🎯."
            b1, b2 = "Click here to earn 0.1$", "➡️ Next Task"
        ikb = types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton(b1, url=link), types.InlineKeyboardButton(b2, callback_data="check_t"))
        bot.send_message(uid, msg, reply_markup=ikb)
    else:
        err = "لم تكتمل المهمة الاولى 🚩❌" if u[6]=='ar' else "Task not completed yet 🚩❌"
        bot.answer_callback_query(call.id, err, show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "w_u")
def w_u(call):
    u = get_user(str(call.message.chat.id))
    if u[2] < 10.0: 
        err_msg = "الحد الأدنى للسحب هو 10$" if u[6]=='ar' else "Minimum withdrawal is 10$"
        bot.answer_callback_query(call.id, err_msg, show_alert=True)
    else:
        prompt = "يرجى إدخال عنوان محفظتك 💸💰." if u[6]=='ar' else "Please enter your wallet address 💸💰."
        m = bot.send_message(call.message.chat.id, prompt)
        bot.register_next_step_handler(m, process_final_withdrawal, u[6])

def process_final_withdrawal(m, lang):
    admin_bot.send_message(MY_ID, f"Withdraw Request!\nUID: {m.chat.id}\nWallet: {m.text}")
    confirm = "لقد تلقينا طلبك ستصل لك أموالك في غضون 24 ساعة بعدها مراجعة الطلب ⏳💸." if lang=='ar' else "We have received your request, your money will arrive within 24 hours after reviewing the request ⏳💸."
    bot.send_message(m.chat.id, confirm)

bot.polling(none_stop=True)
