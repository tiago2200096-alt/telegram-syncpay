import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import threading
import time

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

# ================== MEDIA ==================
MEDIA = {
    "WELCOME_VIDEO": "https://res.cloudinary.com/declnidxc/video/upload/v1770453000/lv_0_20260128120445_ltxyrw.mp4",

    "DATA_VIDEO": "https://res.cloudinary.com/declnidxc/video/upload/v1770453000/lv_0_20260128120445_ltxyrw.mp4",

    "PAYMENT_VIDEO": "https://res.cloudinary.com/declnidxc/video/upload/v1770454441/lv_0_20260207055140_obfflt.mp4",

    "DELAY_VIDEO": "https://res.cloudinary.com/declnidxc/video/upload/v1776976877/lv_0_20260423173934_rzcqdg.mp4"
}

# ================== MENU ==================
def menu():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📅 Plano Mensal", callback_data="mensal"))
    kb.add(InlineKeyboardButton("💎 Plano Vitalício", callback_data="vitalicio"))
    kb.add(InlineKeyboardButton("🆘 Suporte", url="https://t.me/anonimoprimevip"))
    return kb

# ================== START ==================
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_video(
        message.chat.id,
        MEDIA["WELCOME_VIDEO"],
        caption=(
            "🔥 *Bem-vindo ao BrasilPrime VIP* 🔥\n\n"
            "💎 Conteúdo exclusivo que você não encontra fácil...\n\n"
            "✨ OnlyFans / Privacy\n"
            "🔥 Conteúdos +18 BR\n"
            "🎥 Vídeos raros\n"
            "💋 Muito mais...\n\n"
            "👇 Escolha seu plano:"
        ),
        reply_markup=menu()
    )

# ================== CALLBACKS ==================
@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):

    if call.data == "mensal":
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("💳 Assinar Mensal", callback_data="pagar_mensal"))
        kb.add(InlineKeyboardButton("⬅️ Voltar", callback_data="voltar"))

        bot.send_message(
            call.message.chat.id,
            "📅 *Plano Mensal*\n\n💰 Apenas *R$ 29,90*",
            reply_markup=kb
        )

    elif call.data == "vitalicio":
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("💎 Assinar Vitalício", callback_data="pagar_vitalicio"))
        kb.add(InlineKeyboardButton("⬅️ Voltar", callback_data="voltar"))

        bot.send_message(
            call.message.chat.id,
            "💎 *Plano Vitalício*\n\n🔥 De *R$197* por *R$97*",
            reply_markup=kb
        )

    elif call.data == "voltar":
        bot.send_message(call.message.chat.id, "Escolha um plano:", reply_markup=menu())

    elif call.data in ["pagar_mensal", "pagar_vitalicio"]:
        iniciar_fluxo(call.message)

# ================== FLUXO ==================
def iniciar_fluxo(message):

    bot.send_video(
        message.chat.id,
        MEDIA["DATA_VIDEO"],
        caption="🔐 Digite seu CPF:"
    )

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

    bot.send_video(
        message.chat.id,
        MEDIA["PAYMENT_VIDEO"],
        caption="💰 Finalize o pagamento via Pix 👇",
        reply_markup=kb
    )

    # DISPARO AUTOMÁTICO (delay)
    threading.Thread(target=delay_video, args=(message.chat.id,)).start()


def delay_video(chat_id):
    time.sleep(120)  # 2 minutos
    bot.send_video(
        chat_id,
        MEDIA["DELAY_VIDEO"],
        caption="⚡ Falta pouco... finalize o pagamento para liberar o acesso!"
    )

# ================== RUN ==================
def run_bot():
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
