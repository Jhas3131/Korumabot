import time
from pyrogram import Client, filters, enums
from pyrogram.types import ChatPermissions

# --- SENİN BİLGİLERİN ---
API_ID = 32534149
API_HASH = "35e7e6f29c4b100fb13fc86cc6badf62"
BOT_TOKEN = "8790422575:AAHFW_i-hLXxzTyflaOTSPCUiV8nI6q3UKs"
SUPER_ADMIN_ID = 7738591317 

# --- SİSTEM DEĞİŞKENLERİ ---
is_active = True
start_time = time.time()
admin_logs = {}
LIMIT_COUNT = 3
LIMIT_SECONDS = 60

app = Client("guard_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def get_uptime():
    diff = int(time.time() - start_time)
    days, rem = divmod(diff, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{days} Gün, {hours} Saat, {minutes} Dakika, {seconds} Saniye"

@app.on_message(filters.command("ac") & filters.user(SUPER_ADMIN_ID))
async def open_bot(_, message):
    global is_active
    is_active = True
    await message.reply_text("✅ Koruma AKTİF.")

@app.on_message(filters.command("kapat") & filters.user(SUPER_ADMIN_ID))
async def close_bot(_, message):
    global is_active
    is_active = False
    await message.reply_text("⚠️ Koruma KAPALI.")

@app.on_message(filters.command("durum"))
async def status_bot(_, message):
    status = "🟢 AKTİF" if is_active else "🔴 KAPALI"
    await message.reply_text(f"📊 Durum: {status}\n⏱ Süre: {get_uptime()}")

@app.on_chat_member_updated()
async def track_bans(client, update):
    global is_active
    if not is_active: return
    if update.new_chat_member and update.new_chat_member.status == enums.ChatMemberStatus.BANNED:
        from_user = update.from_user
        if not from_user or from_user.id == SUPER_ADMIN_ID: return
        admin_id = from_user.id
        current_time = time.time()
        if admin_id not in admin_logs: admin_logs[admin_id] = []
        admin_logs[admin_id] = [t for t in admin_logs[admin_id] if current_time - t < LIMIT_SECONDS]
        admin_logs[admin_id].append(current_time)
        if len(admin_logs[admin_id]) > LIMIT_COUNT:
            try:
                await client.restrict_chat_member(update.chat.id, admin_id, ChatPermissions(can_send_messages=False))
                await client.send_message(update.chat.id, f"🚨 Admin {from_user.mention} yetkileri alındı.")
                try: await client.send_message(admin_id, "🤠 iyi denemeydi")
                except: pass
                admin_logs[admin_id] = []
            except: pass

print("Bot başlatılıyor...")
app.run()
