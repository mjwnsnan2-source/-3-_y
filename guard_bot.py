from pyrogram import Client, filters
from pyrogram.types import ChatPermissions
from collections import defaultdict
import time
import re

API_ID = 123456
API_HASH = "YOUR_API_HASH"
BOT_TOKEN = "YOUR_BOT_TOKEN"

app = Client(
    "guard_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# إعدادات
FLOOD_LIMIT = 8
FLOOD_WINDOW = 10
MUTE_TIME = 300
WARN_LIMIT = 3

# بيانات مؤقتة
warns = defaultdict(int)
user_messages = defaultdict(list)

URL_RE = re.compile(r"(https?://|www\.)")

async def is_admin(chat_id, user_id):
    member = await app.get_chat_member(chat_id, user_id)
    return member.status in ("administrator", "owner")

@app.on_message(filters.command("ping"))
async def ping(_, message):
    await message.reply("✅ البوت يعمل")

@app.on_message(filters.command("warn") & filters.group)
async def warn_handler(_, message):
    if not message.reply_to_message:
        return

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    target = message.reply_to_message.from_user.id

    warns[(message.chat.id, target)] += 1

    count = warns[(message.chat.id, target)]

    await message.reply(f"⚠️ تحذير رقم {count}")

    if count >= WARN_LIMIT:
        await app.ban_chat_member(
            message.chat.id,
            target
        )

        await message.reply(
            "🚫 تم حظر العضو بعد تجاوز حد التحذيرات"
        )

@app.on_message(filters.group)
async def protection(_, message):

    if not message.from_user:
        return

    user_id = message.from_user.id
    chat_id = message.chat.id

    # تجاهل المشرفين
    if await is_admin(chat_id, user_id):
        return

    # منع الروابط
    if message.text and URL_RE.search(message.text):
        try:
            await message.delete()
            return
        except Exception:
            pass

    # مكافحة الإغراق
    now = time.time()

    user_messages[(chat_id, user_id)].append(now)

    user_messages[(chat_id, user_id)] = [
        t for t in user_messages[(chat_id, user_id)]
        if now - t <= FLOOD_WINDOW
    ]

    if len(user_messages[(chat_id, user_id)]) > FLOOD_LIMIT:

        try:
            await app.restrict_chat_member(
                chat_id,
                user_id,
                ChatPermissions(),
                until_date=int(now + MUTE_TIME)
            )

            await message.reply(
                "🚫 تم كتم العضو مؤقتاً بسبب الإغراق"
            )

            user_messages[(chat_id, user_id)] = []

        except Exception:
            pass

app.run()
