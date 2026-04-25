import os
import telebot

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "✅ Bot pronto.\n\n"
        "Agora me adicione no grupo VIP como admin e mande qualquer mensagem lá."
    )


@bot.message_handler(func=lambda message: True, content_types=["text"])
def pegar_chat_id(message):
    bot.send_message(
        message.chat.id,
        f"📌 *CHAT ID encontrado:*\n\n`{message.chat.id}`\n\n"
        f"Tipo: `{message.chat.type}`"
    )

    print("CHAT ID:", message.chat.id)
    print("CHAT TYPE:", message.chat.type)


def run_bot():
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)


if __name__ == "__main__":
    run_bot()
