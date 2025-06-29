import os
import logging
import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from utils import add_user, increment_files_shared, get_stats, load_data

# --- Config ---
BOT_TOKEN = "8138100267:AAElyCZzoZHAFP_2lVG9ABQbQIf2__7Y1QE"
BOT_NAME = "ShareToLinkBot"
DEVELOPER_USERNAME = "lurhe"
ADMIN_ID = 7775062794  # Replace with your Telegram ID
TEMP_DIR = "temp_files"
os.makedirs(TEMP_DIR, exist_ok=True)

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Start Command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id)
    welcome_text = (
        f"👋 Hello {update.effective_user.first_name}!
\n"
        f"Welcome to *{BOT_NAME}*.
\n"
        "📂 Send me any file and I’ll generate a temporary download link using file.io."
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📄 Help", callback_data='help')],
        [InlineKeyboardButton("ℹ️ About", callback_data='about')],
        [InlineKeyboardButton("🧑‍💻 Developer", url=f"https://t.me/{DEVELOPER_USERNAME}")]
    ])
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=keyboard)

# --- Help & About ---
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'help':
        await query.edit_message_text(
            "📄 *How to Use ShareToLinkBot:*\n\n"
            "1. Send any file\n"
            "2. I’ll upload it to file.io\n"
            "3. You’ll get a private download link (auto-expiring)",
            parse_mode="Markdown"
        )
    elif query.data == 'about':
        await query.edit_message_text(
            "ℹ️ *About ShareToLinkBot:*\n\n"
            "This bot turns your uploaded files into shareable temporary links using file.io.\n"
            "Built by [@lurhe](https://t.me/lurhe)",
            parse_mode="Markdown"
        )

# --- File Upload ---
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document or update.message.video or update.message.photo[-1]
    file_info = await file.get_file()
    filename = getattr(file, 'file_name', f"{file_info.file_id}.bin")
    filepath = os.path.join(TEMP_DIR, filename)

    await file_info.download_to_drive(filepath)
    add_user(update.effective_user.id)
    increment_files_shared()

    with open(filepath, "rb") as f:
        response = requests.post("https://file.io", files={"file": f})

    if response.ok:
        link = response.json().get("link")
        await update.message.reply_text(f"✅ File uploaded successfully!\n📎 One-time download link:\n{link}")
    else:
        await update.message.reply_text("❌ Failed to upload file to file.io. Try again later.")

    os.remove(filepath)

# --- Broadcast ---
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("🚫 You are not authorized to use this.")
    if not context.args:
        return await update.message.reply_text("❗ Usage: /broadcast Your message here")

    message = " ".join(context.args)
    count = 0
    for user_id in load_data()["users"]:
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
            count += 1
        except:
            pass
    await update.message.reply_text(f"✅ Broadcast sent to {count} users.")

# --- Status ---
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("🚫 You are not authorized to use this.")
    users, files = get_stats()
    await update.message.reply_text(f"📈 Bot Status:\n\n👥 Users: {users}\n📁 Files Shared: {files}")

# --- Main ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.Video.ALL | filters.PHOTO, handle_file))
    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
