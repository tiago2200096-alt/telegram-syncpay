import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import threading
import time

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

# ================== MÍDIAS ==================
MEDIA = {
    "WELCOME_VIDEO": "https://res.cloudinary.com/declnidxc/video/upload/v1770453000/lv_0_20260128120445_ltxyrw.mp4",

    "DATA_VIDEO": "https://res.cloudinary.com/declnidxc/video/upload/v1770453000/lv_0_20260128120445_ltxyrw.mp4",

    "PAYMENT_VIDEO": "https://res.cloudinary.com/declnidxc/video/upload/v1770454441/lv_0_20260207055140_obfflt.mp4",

    "DELAY_VIDEO": "https://res.cloudinary.com/declnidxc/video/upload/v1776976877/lv_0_20260423173934_rzcqdg.mp4"
}
}

# ================== MEMÓRIA SIMPLES ==================
user_data = {}

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
            "💎 Conteúdos exclusivos que você NÃO encontra fácil...\n\n"
            "*Você vai ter acesso a:*\n"
            "✨ OnlyFans / Privacy\n"
            "🔥 Ninfetas +18\n"
            "🕶️ Conteúdos ocultos\n"
            "🎥 Vídeos raros\n"
            "💋 Muito mais...\n\n"
            "👇 *Escolha seu plano abaixo:*"
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
            "📅 *Plano Mensal*\n\n"
            "Acesso completo ao VIP.\n\n"
            "💰 *Apenas R$ 29,90*",
            reply_markup=kb
        )

    elif call.data == "vitalicio":
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("💎 Assinar Vitalício", callback_data="pagar_vitalicio"))
        kb.add(InlineKeyboardButton("⬅️ Voltar", callback_data="voltar"))

        bot.send_message(
            call.message.chat.id,
            "💎 *Plano Vitalício*\n\n"
            "🔥 Oferta única\n\n"
            "De ~R$197~ por *R$97*\n\n"
            "Acesso pra sempre.",
            reply_markup=kb
        )

    elif call.data == "voltar":
        bot.send_message(call.message.chat.id, "Escolha um plano:", reply_markup=menu())

    elif call.data in ["pagar_mensal", "pagar_vitalicio"]:
        user_data[call.message.chat.id] = {"step": "cpf", "plano": call.data}

        bot.send_video(
            call.message.chat.id,
            MEDIA["DATA_VIDEO"],
            caption="🔐 Digite seu CPF para continuar:"
        )

    elif call.data == "verificar":
        bot.send_message(
            call.message.chat.id,
            "⏳ Estamos verificando seu pagamento...\n\nSe já pagou, aguarde ou fale com suporte."
        )

# ================== FLUXO DE DADOS ==================
@bot.message_handler(func=lambda message: True)
def receber_dados(message):
    user = user_data.get(message.chat.id)

    if not user:
        return

    if user["step"] == "cpf":
        user["cpf"] = message.text
        user["step"] = "telefone"
        bot.send_message(message.chat.id, "📱 Digite seu telefone com DDD:")

    elif user["step"] == "telefone":
        user["telefone"] = message.text
        user["step"] = "email"
        bot.send_message(message.chat.id, "📧 Digite seu e-mail:")

    elif user["step"] == "email":
        user["email"] = message.text
        user["step"] = "done"

        gerar_pagamento(message.chat.id)

# ================== PAGAMENTO ==================
def gerar_pagamento(chat_id):

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Já paguei (verificar)", callback_data="verificar"))
    kb.add(InlineKeyboardButton("🆘 Suporte", url="https://t.me/anonimoprimevip"))

    bot.send_video(
        chat_id,
        MEDIA["PAYMENT_VIDEO"],
        caption=(
            "💳 *Pagamento gerado!*\n\n"
            "Finalize para liberar seu acesso.\n\n"
            "👇 Depois clique abaixo"
        ),
        reply_markup=kb
    )

    # 🔥 Lembrete automático após 2 minutos
    def lembrete():
        time.sleep(120)

        bot.send_video(
            chat_id,
            MEDIA["REMINDER_VIDEO"],
            caption="⚡ Falta só concluir o pagamento pra liberar seu acesso."
        )

    threading.Thread(target=lembrete).start()

# ================== RUN ==================
def run_bot():
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True, timeout=20, long_polling_timeout=20)
