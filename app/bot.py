import os
import time
import uuid
import threading
import requests
import telebot
import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("TELEGRAM_TOKEN")
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")

GROUP_ID = -1003700780254

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

START_VIDEO = "BAACAgEAAxkBAANYaevr3T0Iu0WHTcsjBZ1Jo6F4liUAAjEKAAKEtmFHYy-juZDqFfc7BA"
PAGAMENTO_VIDEO = "BAACAgEAAxkBAANuaev6AAFn46WIeaF5ZnI9bAtmV8PNAAI3CgAChLZhR-BxvRomfgSuOwQ"
PIX_VIDEO = "BAACAgEAAxkBAANyaev7PxnIlAdjn4RqriaUhyrQRsgAAjkKAAKEtmFHKaMw9RQPQFk7BA"
LEMBRETE_VIDEO = "BAACAgEAAxkBAAN0aev7X6Sfrq3QaJ6qpaZWjHP5y44AAjoKAAKEtmFHeTo0KucnbJg7BA"


def plano_info(plano):
    if plano == "mensal":
        return "Plano Mensal", 0.50
    return "Plano Vitalício", 0.80


def gerar_link_temporario():
    expire_date = int((datetime.datetime.now() + datetime.timedelta(minutes=10)).timestamp())

    link = bot.create_chat_invite_link(
        chat_id=GROUP_ID,
        member_limit=1,
        expire_date=expire_date
    )

    return link.invite_link


def criar_pix(valor, email, cpf, nome):
    headers = {
        "Authorization": f"Bearer {MP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Idempotency-Key": str(uuid.uuid4())
    }

    payload = {
        "transaction_amount": float(valor),
        "payment_method_id": "pix",
        "description": "Acesso VIP",
        "payer": {
            "email": email,
            "first_name": nome,
            "identification": {
                "type": "CPF",
                "number": cpf
            }
        }
    }

    r = requests.post("https://api.mercadopago.com/v1/payments", json=payload, headers=headers)
    r.raise_for_status()
    return r.json()


def consultar(payment_id):
    r = requests.get(
        f"https://api.mercadopago.com/v1/payments/{payment_id}",
        headers={"Authorization": f"Bearer {MP_ACCESS_TOKEN}"}
    )
    return r.json()


user = {}
payments = {}


@bot.message_handler(commands=["start"])
def start(m):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📅 Mensal", callback_data="mensal"))
    kb.add(InlineKeyboardButton("💎 Vitalício", callback_data="vitalicio"))

    bot.send_video(m.chat.id, START_VIDEO, caption="🔥 Escolha seu plano:", reply_markup=kb)


@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    if c.data in ["mensal", "vitalicio"]:
        user[c.message.chat.id] = {"plano": c.data}
        bot.send_message(c.message.chat.id, "Digite seu CPF:")

    elif c.data.startswith("check_"):
        pid = c.data.split("_")[1]
        status = consultar(pid).get("status")

        if status == "approved":
            link = gerar_link_temporario()
            bot.send_message(c.message.chat.id, "✅ Pago! Acesse 👇")
            bot.send_message(c.message.chat.id, link)
        else:
            bot.send_message(c.message.chat.id, "⏳ Ainda não confirmado.")


@bot.message_handler(func=lambda m: True)
def fluxo(m):
    u = user.get(m.chat.id)

    if not u:
        return

    if "cpf" not in u:
        u["cpf"] = m.text
        bot.send_message(m.chat.id, "Agora email:")
    elif "email" not in u:
        u["email"] = m.text

        nome, valor = plano_info(u["plano"])
        p = criar_pix(valor, u["email"], u["cpf"], m.from_user.first_name)

        pid = str(p["id"])
        payments[pid] = m.chat.id

        pix = p["point_of_interaction"]["transaction_data"]["qr_code"]

        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("✅ Já paguei", callback_data=f"check_{pid}"))

        bot.send_video(m.chat.id, PIX_VIDEO, caption=f"💰 Pague R$ {valor}", reply_markup=kb)
        bot.send_message(m.chat.id, pix, parse_mode=None)


bot.infinity_polling()
