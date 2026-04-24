import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import threading
import time

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

WELCOME_VIDEO = "https://res.cloudinary.com/declnidxc/video/upload/v1770453000/lv_0_20260128120445_ltxyrw.mp4"


def menu():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📅 Plano Mensal", callback_data="mensal"))
    kb.add(InlineKeyboardButton("💎 Plano Vitalício", callback_data="vitalicio"))
    kb.add(InlineKeyboardButton("🆘 Suporte", url="https://t.me/anonimoprimevip"))
    return kb


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "🔥 *Bem-vindo ao BrasilPrime VIP* 🔥\n\n"
        "💎 Conteúdo exclusivo que você não encontra fácil...\n\n"
        "✨ OnlyFans / Privacy\n"
        "🔥 Conteúdos +18 BR\n"
        "🎥 Vídeos raros\n"
        "💋 Muito mais...\n\n"
        "👇 Escolha seu plano:",
        reply_markup=menu()
    )

    try:
        bot.send_video(
            message.chat.id,
            WELCOME_VIDEO,
            caption="🎥 *Veja o que te espera no VIP.*"
        )
    except Exception as e:
        print("Erro ao enviar vídeo de start:", e)


@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):

    if call.data == "mensal":
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("💳 Assinar Mensal", callback_data="pagar"))
        kb.add(InlineKeyboardButton("⬅️ Voltar", callback_data="voltar"))

        bot.send_message(
            call.message.chat.id,
            "📅 *Plano Mensal*\n\n💰 Apenas *R$ 29,90*",
            reply_markup=kb
        )

    elif call.data == "vitalicio":
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("💎 Assinar Vitalício", callback_data="pagar"))
        kb.add(InlineKeyboardButton("⬅️ Voltar", callback_data="voltar"))

        bot.send_message(
            call.message.chat.id,
            "💎 *Plano Vitalício*\n\n🔥 De *R$197* por *R$97*",
            reply_markup=kb
        )

    elif call.data == "voltar":
        bot.send_message(call.message.chat.id, "Escolha um plano:", reply_markup=menu())

    elif call.data == "pagar":
        iniciar_fluxo(call.message)


def iniciar_fluxo(message):
    bot.send_message(message.chat.id, "🔐 Digite seu CPF:")
    bot.register_next_step_handler(message, pegar_cpf)


def pegar_cpf(message):
    bot.send_message(message.chat.id, "📱 Agora seu telefone com DDD:")
    bot.register_next_step_handler(message, pegar_telefone)


def pegar_telefone(message):
    bot.send_message(message.chat.id, "📧 Agora seu email:")
    bot.register_next_step_handler(message, gerar_pagamento)


def gerar_pagamento(message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Já paguei (verificar)", callback_data="verificar"))
    kb.add(InlineKeyboardButton("🆘 Suporte", url="https://t.me/anonimoprimevip"))

    bot.send_message(
        message.chat.id,
        "💰 *Pagamento gerado!*\n\n"
        "Finalize o Pix para liberar seu acesso.\n\n"
        "Depois clique em *Já paguei (verificar)* 👇",
        reply_markup=kb
    )

    threading.Thread(target=lembrete, args=(message.chat.id,), daemon=True).start()


def lembrete(chat_id):
    time.sleep(120)
    bot.send_message(
        chat_id,
        "⚡ Falta pouco... finalize o pagamento para entrar no VIP!"
    )


def run_bot():
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)


if __name__ == "__main__":
    run_bot()
