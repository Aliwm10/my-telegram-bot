from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
import json
import os

TOKEN = "7628523529:AAHkK7r6x_PgckkosO84mT_1Tq26M-PVrJw"
OWNER_ID = 1866797115

DATA_FILE = "user_data.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        user_data = json.load(f)
else:
    user_data = {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(user_data, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # هر بار که /start زده شد پیام خوش آمدگویی بفرست
    await update.message.reply_text(
        "سلام 👋\n\nپیامت رو بفرست اینجا، من میفرستم برای صاحب این بات.\n\nبعدش منتظر باش هر وقت پاسخ داد اینجا بهت نشون میدم."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    text = update.message.text

    if user_id not in user_data:
        user_data[user_id] = {"started": True, "sent_first_message": False}
        save_data()
        await update.message.reply_text(
            "سلام 👋\n\nپیامت رو بفرست اینجا، من میفرستم برای صاحب این بات.\n\nبعدش منتظر باش هر وقت پاسخ داد اینجا بهت نشون میدم."
        )
        return

    user_info = f"👤 کاربر:\nنام: {user.first_name}\nآیدی عددی: {user.id}\nیوزرنیم: @{user.username if user.username else 'ندارد'}"
    await context.bot.send_message(chat_id=OWNER_ID, text=user_info)

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("پاسخ دادن", callback_data=f"reply_{user_id}")]]
    )
    sent_message = await context.bot.send_message(chat_id=OWNER_ID, text=text, reply_markup=keyboard)

    if not user_data[user_id]["sent_first_message"]:
        await update.message.reply_text("پیام به صاحب بات منتقل شد ✅\n\nمنتظر باشید هر جواب داد پاسخ رو همینجا دریافت میکنید.")
        await update.message.reply_text(
            "نکته مهم 💡\n\nبرای پیام‌های بعدی که ارسال می‌کنید دیگه نمیگم \"پیام ارسال شد\" اما در اصل پیام منتقل میشه (مثل چت معمولی)"
        )
        user_data[user_id]["sent_first_message"] = True
        save_data()

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("reply_"):
        user_id = query.data.split("_")[1]

        context.user_data["reply_to"] = user_id
        await query.message.reply_text(f"پیام خودت رو برای پاسخ به کاربر {user_id} اینجا بفرست.")

async def reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if "reply_to" in context.user_data:
        to_user_id = context.user_data["reply_to"]
        text = update.message.text

        try:
            await context.bot.send_message(chat_id=int(to_user_id), text=f"💬 پاسخ صاحب بات:\n\n{text}")
            await update.message.reply_text("پیام شما ارسال شد ✅")
        except Exception as e:
            await update.message.reply_text(f"خطا در ارسال پیام: {e}")

        context.user_data.pop("reply_to")
    else:
        await handle_message(update, context)

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("دستور ناشناخته است.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), reply_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    print("Bot is running...")
    app.run_polling()
