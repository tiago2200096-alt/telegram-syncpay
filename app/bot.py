import os
import time
import uuid
import threading
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("TELEGRAM_TOKEN")
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")
VIP_INVITE_LINK = os.getenv("VIP_INVITE_LINK", "https://t.me/anonimoprimevip")

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

START_VIDEO = "BAACAgEAAxkBAANYaevr3T0Iu0WHTcsjBZ1Jo6F4liUAAjEKAAKEtmFHYy-juZDqFfc7BA"
PAGAMENTO_VIDEO = "BAACAgEAAxkBAANuaev6AAFn46WIeaF5ZnI9bAtmV8PNAAI3CgAChLZhR-BxvRomfgSuOwQ"
PIX_VIDEO = "BAACAgEAAxkBAANyaev7PxnIlAdjn4RqriaUhyrQRsgAAjkKAAKEtmFHKaMw9RQPQFk7BA"
LEMBRETE_VIDEO = "BAACAgEAAxkBAAN0aev7X6Sfrq3QaJ6qpaZWjHP5y44AAjoKAAKEtmFHeTo0KucnbJg7BA"

SUPORTE = "https://t.me/anonimoprimevip"

user_states = {}
user_data = {}
payments = {}


def menu():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📅 Plano Mensal", callback_data="mensal"))
    kb.add(InlineKeyboardButton("💎 Plano Vitalício", callback_data="vitalicio"))
    kb.add(InlineKeyboardButton("🆘 Suporte", url=SUPORTE))
    return kb


# 💰 VALORES DE TESTE
def plano_info(plano):
    if plano == "mensal":
        return "Plano Mensal", 0.50
    return "Plano Vitalício", 0.80


def criar_pix_mp(plano, cpf, email, nome):
    nome_plano, valor = plano_info(plano)

    headers = {
        "Authorization": f"Bearer {MP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Idempotency-Key": str(uuid.uuid4())
    }

    payload = {
        "transaction_amount": float(valor),
        "description": nome_plano,
        "payment_method_id": "pix",
        "payer": {
            "email": email,
            "first_name": nome or "Cliente",
            "identification": {
                "type": "CPF",
                "number": cpf
            }
        }
    }

    r = requests.post(
        "https://api.mercadopago.com/v1/payments",
        json=payload,
        headers=headers,
        timeout=30
    )
    r.raise_for_status()
    return r.json()


def consultar_pagamento(payment_id):
    headers = {"Authorization": f"Bearer {MP_ACCESS_TOKEN}"}

    r = requests.get(
        f"https://api.mercadopago.com/v1/payments/{payment_id}",
        headers=headers,
        timeout=30
    )
    r.raise_for_status()
    return r.json()


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_video(
        message.chat.id,
        START_VIDEO,
        caption=(
            "🔥 *Bem-vindo ao BrasilPrime VIP* 🔥\n\n"
            "💎 Conteúdo exclusivo que você não encontra fácil...\n\n"
            "✨ Conteúdos premium\n"
            "🔥 Atualizações frequentes\n"
            "🎥 Vídeos raros\n"
            "💋 Muito mais...\n\n"
            "👇 Escolha seu plano:"
        ),
        reply_markup=menu()
    )


@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):

    if call.data == "mensal":
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("💳 Assinar Mensal", callback_data="pagar_mensal"))
        kb.add(InlineKeyboardButton("⬅️ Voltar", callback_data="voltar"))

        bot.send_message(
            call.message.chat.id,
            "📅 *Plano Mensal*\n\n💰 Apenas *R$ 0,50*",
            reply_markup=kb
        )

    elif call.data == "vitalicio":
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("💎 Assinar Vitalício", callback_data="pagar_vitalicio"))
        kb.add(InlineKeyboardButton("⬅️ Voltar", callback_data="voltar"))

        bot.send_message(
            call.message.chat.id,
            "💎 *Plano Vitalício*\n\n💰 Apenas *R$ 0,80*",
            reply_markup=kb
        )

    elif call.data == "voltar":
        bot.send_message(call.message.chat.id, "📌 Escolha seu plano:", reply_markup=menu())

    elif call.data == "pagar_mensal":
        iniciar_fluxo(call.message, "mensal")

    elif call.data == "pagar_vitalicio":
        iniciar_fluxo(call.message, "vitalicio")

    elif call.data.startswith("verificar_"):
        payment_id = call.data.replace("verificar_", "")
        verificar_pagamento(call.message, payment_id)


def iniciar_fluxo(message, plano):
    user_id = message.chat.id
    user_states[user_id] = "cpf"
    user_data[user_id] = {"plano": plano}

    bot.send_video(
        message.chat.id,
        PAGAMENTO_VIDEO,
        caption="Digite seu *CPF* para gerar o Pix:"
    )


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.chat.id

    if user_id not in user_states:
        return

    estado = user_states[user_id]

    if estado == "cpf":
        user_data[user_id]["cpf"] = "".join(filter(str.isdigit, message.text))
        user_states[user_id] = "telefone"
        bot.send_message(message.chat.id, "📱 Envie seu telefone:")

    elif estado == "telefone":
        user_data[user_id]["telefone"] = message.text
        user_states[user_id] = "email"
        bot.send_message(message.chat.id, "📧 Envie seu e-mail:")

    elif estado == "email":
        user_data[user_id]["email"] = message.text
        user_states[user_id] = "finalizado"
        gerar_pagamento(message)


def gerar_pagamento(message):
    user_id = message.chat.id
    dados = user_data[user_id]

    try:
        pagamento = criar_pix_mp(
            plano=dados["plano"],
            cpf=dados["cpf"],
            email=dados["email"],
            nome=message.from_user.first_name
        )
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "❌ Erro ao gerar Pix")
        return

    payment_id = str(pagamento["id"])
    transaction_data = pagamento["point_of_interaction"]["transaction_data"]

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Já paguei / verificar", callback_data=f"verificar_{payment_id}"))

    bot.send_video(
        message.chat.id,
        PIX_VIDEO,
        caption="💰 Pix gerado! Pague e clique abaixo 👇",
        reply_markup=kb
    )

    bot.send_message(
        message.chat.id,
        f"📌 PIX:\n\n{transaction_data['qr_code']}",
        parse_mode=None
    )

    threading.Thread(target=lembrete, args=(message.chat.id, payment_id), daemon=True).start()


def verificar_pagamento(message, payment_id):
    pagamento = consultar_pagamento(payment_id)
    status = pagamento.get("status")

    if status == "approved":
        bot.send_message(message.chat.id, "✅ Pagamento aprovado!")
        bot.send_message(message.chat.id, VIP_INVITE_LINK)

    else:
        bot.send_message(message.chat.id, "⏳ Ainda não confirmado.")


def lembrete(chat_id, payment_id):
    time.sleep(120)
    bot.send_video(chat_id, LEMBRETE_VIDEO, caption="⚡ Finalize o pagamento!")


def run_bot():
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)


if __name__ == "__main__":
    run_bot()
