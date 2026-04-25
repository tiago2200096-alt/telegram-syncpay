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


def plano_info(plano):
    if plano == "mensal":
        return "Plano Mensal", 29.90
    return "Plano Vitalício", 97.00


def criar_pix_mp(plano, cpf, email, nome):
    nome_plano, valor = plano_info(plano)

    url = "https://api.mercadopago.com/v1/payments"

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

    r = requests.post(url, json=payload, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()


def consultar_pagamento(payment_id):
    url = f"https://api.mercadopago.com/v1/payments/{payment_id}"
    headers = {
        "Authorization": f"Bearer {MP_ACCESS_TOKEN}"
    }

    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_video(
        message.chat.id,
        START_VIDEO,
        caption=(
            "🔥 *Bem-vindo ao BrasilPrime VIP* 🔥\n\n"
            "💎 Conteúdo adulto +18 exclusivo e difícil de encontrar.\n\n"
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
            "📅 *Plano Mensal*\n\n"
            "✅ Acesso ao grupo VIP\n"
            "✅ Conteúdos exclusivos\n"
            "✅ Suporte direto\n\n"
            "💰 Apenas *R$ 29,90*",
            reply_markup=kb
        )

    elif call.data == "vitalicio":
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("💎 Assinar Vitalício", callback_data="pagar_vitalicio"))
        kb.add(InlineKeyboardButton("⬅️ Voltar", callback_data="voltar"))

        bot.send_message(
            call.message.chat.id,
            "💎 *Plano Vitalício*\n\n"
            "✅ Acesso permanente\n"
            "✅ Conteúdo premium liberado\n"
            "✅ Sem mensalidade\n\n"
            "🔥 De *R$197* por *R$97*",
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
        caption=(
            "🔐 *Etapa de segurança*\n\n"
            "Seus dados são usados somente para gerar o Pix com segurança.\n\n"
            "Digite seu *CPF* para continuar:"
        )
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

        bot.send_message(message.chat.id, "📱 Agora envie seu *telefone com DDD*:")

    elif estado == "telefone":
        user_data[user_id]["telefone"] = message.text.strip()
        user_states[user_id] = "email"

        bot.send_message(message.chat.id, "📧 Agora envie seu *e-mail*:")

    elif estado == "email":
        user_data[user_id]["email"] = message.text.strip()
        user_states[user_id] = "finalizado"

        gerar_pagamento(message)


def gerar_pagamento(message):
    user_id = message.chat.id
    dados = user_data[user_id]

    plano = dados["plano"]
    nome_plano, valor = plano_info(plano)

    try:
        pagamento = criar_pix_mp(
            plano=plano,
            cpf=dados["cpf"],
            email=dados["email"],
            nome=message.from_user.first_name
        )

        payment_id = str(pagamento["id"])

        transaction_data = pagamento.get("point_of_interaction", {}).get("transaction_data", {})
        pix_copia_cola = transaction_data.get("qr_code", "")
        ticket_url = transaction_data.get("ticket_url", "")

        payments[payment_id] = {
            "user_id": user_id,
            "plano": plano,
            "status": "pending"
        }

        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("✅ Já paguei / verificar", callback_data=f"verificar_{payment_id}"))
        kb.add(InlineKeyboardButton("🆘 Suporte", url=SUPORTE))

        bot.send_video(
            message.chat.id,
            PIX_VIDEO,
            caption=(
                "💰 *Pix gerado com sucesso!*\n\n"
                f"📦 Plano: *{nome_plano}*\n"
                f"💵 Valor: *R$ {valor:.2f}*\n\n"
                "Copie o código Pix abaixo e pague no seu banco."
            ),
            reply_markup=kb
        )

        bot.send_message(
            message.chat.id,
            f"📌 PIX COPIA E COLA:\n\n{pix_copia_cola}",
            parse_mode=None
        )

        if ticket_url:
            bot.send_message(message.chat.id, f"🔗 Link de pagamento:\n{ticket_url}", parse_mode=None)

        threading.Thread(target=lembrete, args=(message.chat.id, payment_id), daemon=True).start()

    except Exception as e:
        print("ERRO MERCADO PAGO:", e)
        bot.send_message(
            message.chat.id,
            "❌ *Não consegui gerar o Pix agora.*\n\n"
            "Tente novamente ou fale com o suporte."
        )


def verificar_pagamento(message, payment_id):
    try:
        pagamento = consultar_pagamento(payment_id)
        status = pagamento.get("status")

        if status == "approved":
            payments[payment_id]["status"] = "approved"

            bot.send_message(
                message.chat.id,
                "✅ *Pagamento aprovado!*\n\n"
                "Seu acesso VIP está liberado 👇"
            )

            bot.send_message(message.chat.id, VIP_INVITE_LINK, parse_mode=None)

        elif status == "pending":
            bot.send_message(
                message.chat.id,
                "⏳ *Pagamento ainda pendente.*\n\n"
                "Se você acabou de pagar, aguarde alguns instantes e clique em verificar novamente."
            )

        else:
            bot.send_message(
                message.chat.id,
                f"⚠️ Status do pagamento: `{status}`\n\n"
                "Se precisar, fale com o suporte."
            )

    except Exception as e:
        print("ERRO AO VERIFICAR:", e)
        bot.send_message(
            message.chat.id,
            "❌ Não consegui verificar agora. Tente novamente em instantes."
        )


def lembrete(chat_id, payment_id):
    time.sleep(120)

    pedido = payments.get(payment_id)

    if not pedido or pedido.get("status") == "approved":
        return

    bot.send_video(
        chat_id,
        LEMBRETE_VIDEO,
        caption=(
            "⚡ *Falta pouco...*\n\n"
            "Finalize o pagamento agora para liberar seu acesso ao VIP."
        )
    )


def run_bot():
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)


if __name__ == "__main__":
    run_bot()
