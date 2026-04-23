import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")


def menu():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📅 Plano Mensal", callback_data="mensal"))
    kb.add(InlineKeyboardButton("🏆 Plano Anual", callback_data="anual"))
    kb.add(InlineKeyboardButton("🆘 Suporte", url="https://t.me/@anonimoprimevip"))
    return kb


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "🔥 *Bem-vindo ao BrasilPrime VIP*\n\nEscolha um plano abaixo:",
        reply_markup=menu()
    )


@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    if call.data == "mensal":
        bot.send_message(
            call.message.chat.id,
            "📅 *Plano Mensal*\n\nIdeal para começar agora."
        )

    elif call.data == "anual":
        bot.send_message(
            call.message.chat.id,
            "🏆 *Plano Anual*\n\nMelhor custo-benefício."
        )


def run_bot():
    bot.infinity_polling(skip_pending=True)
