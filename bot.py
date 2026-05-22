import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ========== НАСТРОЙКИ ==========
TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "data.json"
# ================================


def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ─── /start ────────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    keyboard = []
    for key, section in data["sections"].items():
        keyboard.append([InlineKeyboardButton(section["title"], callback_data=f"sec:{key}")])

    await update.message.reply_text(
        "📚 <b>Привет! Это твоя база знаний.</b>\n\nВыбери раздел:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ─── Обработчик кнопок ─────────────────────────────────────────────────────────
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()

    parts = query.data.split(":")
    action = parts[0]

    # ── Главное меню ──
    if action == "main":
        keyboard = []
        for key, section in data["sections"].items():
            keyboard.append([InlineKeyboardButton(section["title"], callback_data=f"sec:{key}")])
        await query.edit_message_text(
            "📚 Выбери раздел:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    # ── Раздел → список тем ──
    elif action == "sec":
        sec_key = parts[1]
        section = data["sections"][sec_key]
        keyboard = []
        for topic_key, topic in section["topics"].items():
            keyboard.append(
                [InlineKeyboardButton(topic["title"], callback_data=f"topic:{sec_key}:{topic_key}")]
            )
        keyboard.append([InlineKeyboardButton("⬅️ Главное меню", callback_data="main")])
        await query.edit_message_text(
            f"📂 <b>{section['title']}</b>\n\nВыбери тему:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    # ── Тема → список подтем ──
    elif action == "topic":
        sec_key = parts[1]
        topic_key = parts[2]
        topic = data["sections"][sec_key]["topics"][topic_key]
        keyboard = []
        for sub_key, sub in topic["subtopics"].items():
            keyboard.append(
                [InlineKeyboardButton(sub["title"], callback_data=f"sub:{sec_key}:{topic_key}:{sub_key}")]
            )
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data=f"sec:{sec_key}")])
        await query.edit_message_text(
            f"📖 <b>{topic['title']}</b>\n\nВыбери подтему:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    # ── Подтема → контент ──
    elif action == "sub":
        sec_key = parts[1]
        topic_key = parts[2]
        sub_key = parts[3]
        sub = data["sections"][sec_key]["topics"][topic_key]["subtopics"][sub_key]

        back_btn = InlineKeyboardMarkup(
            [[InlineKeyboardButton("⬅️ Назад", callback_data=f"topic:{sec_key}:{topic_key}")]]
        )
        text = f"📝 <b>{sub['title']}</b>\n\n{sub['content']}"

        if sub.get("photo"):
            await query.message.reply_photo(
                photo=sub["photo"],
                caption=text,
                parse_mode="HTML",
                reply_markup=back_btn,
            )
        else:
            await query.edit_message_text(
                text,
                parse_mode="HTML",
                reply_markup=back_btn,
            )


# ─── Запуск ────────────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("✅ Бот запущен!")
    app.run_polling()


if __name__ == "__main__":
    main()
