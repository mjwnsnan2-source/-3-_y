from pyrogram import Client, filters
from collections import defaultdict
from time import time

# =========================
# ⚙️ إعدادات
# =========================

API_ID = 123456
API_HASH = "API_HASH"
BOT_TOKEN = "8294825532:AAEbsw5KLKy7TAhjmBzSYRSOQ9wdw0ga7sE"

OWNER_ID = 8917441179

# =========================
# 🧠 ذاكرة النظام
# =========================

call_active = defaultdict(bool)
user_activity = defaultdict(list)
risk_score = defaultdict(int)

banned_users = set()
muted_users = set()

# =========================
# 🎥 إدارة المكالمات
# =========================

def start_call(chat_id):
    call_active[chat_id] = True

def stop_call(chat_id):
    call_active[chat_id] = False

def is_call(chat_id):
    return call_active[chat_id]

# =========================
# 🧠 تسجيل النشاط
# =========================

def record(user_id):
    now = time()

    user_activity[user_id].append(now)

    # آخر 10 ثواني فقط
    user_activity[user_id] = [
        t for t in user_activity[user_id]
        if now - t < 10
    ]

# =========================
# 📊 تحليل الذكاء
# =========================

def analyze(user_id):
    activity = len(user_activity[user_id])

    if activity > 15:
        risk_score[user_id] += 40
    elif activity > 10:
        risk_score[user_id] += 25
    elif activity > 5:
        risk_score[user_id] += 10
    else:
        risk_score[user_id] -= 2

    risk_score[user_id] = max(0, risk_score[user_id])

    score = risk_score[user_id]

    if score >= 80:
        return "ban"
    elif score >= 50:
        return "mute"
    elif score >= 20:
        return "warn"
    else:
        return "safe"

# =========================
# 🚨 كشف هجوم جماعي
# =========================

def detect_attack(chat_id):
    total = sum(len(v) for v in user_activity.values())

    if total > 50:
        return "attack"
    return "normal"

# =========================
# 🤖 البوت
# =========================

app = Client(
    "SmartCallSecurity",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# =========================
# 🎥 تشغيل المكالمة
# =========================

@app.on_message(filters.command("تشغيل_المكالمة") & filters.user(OWNER_ID))
async def start_call_cmd(_, message):
    start_call(message.chat.id)
    await message.reply_text("🎥 تم تفعيل وضع حماية المكالمة الذكي")

# =========================
# 🛑 إيقاف المكالمة
# =========================

@app.on_message(filters.command("إيقاف_المكالمة") & filters.user(OWNER_ID))
async def stop_call_cmd(_, message):
    stop_call(message.chat.id)
    await message.reply_text("🛑 تم إيقاف وضع المكالمة")

# =========================
# 🛡️ الحماية العامة
# =========================

@app.on_message(filters.all)
async def protector(_, message):

    user = message.from_user
    if not user:
        return

    uid = user.id
    chat_id = message.chat.id

    # 👑 تجاهل المالك
    if uid == OWNER_ID:
        return

    # 🚫 محظور
    if uid in banned_users:
        return await message.delete()

    # 🎥 فقط أثناء المكالمة
    if not is_call(chat_id):
        return

    # 🧠 تسجيل وتحليل
    record(uid)
    result = analyze(uid)
    attack = detect_attack(chat_id)

    # 🚨 هجوم جماعي
    if attack == "attack":
        await message.reply_text("🚨 تم اكتشاف هجوم أثناء المكالمة!")

    # 🚫 قرارات النظام
    if result == "ban":
        banned_users.add(uid)
        await message.delete()
        await message.reply_text("🚫 تم حظرك (AI Security System)")

    elif result == "mute":
        muted_users.add(uid)
        await message.delete()
        await message.reply_text("🔇 تم كتمك أثناء المكالمة")

    elif result == "warn":
        await message.reply_text("⚠️ توقف عن الإرسال أثناء المكالمة")

# =========================
# 🚀 تشغيل البوت
# =========================

print("🧠 Smart Call Security Bot is running...")
app.run()