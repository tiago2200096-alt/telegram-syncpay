import os
import time
import threading
from io import BytesIO

import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

SUPORTE_LINK = "https://t.me/anonimoprimevip"

SYNC_BASE_URL = os.getenv("SYNC_BASE_URL", "https://api.syncpayments.com.br").rstrip("/")
SYNC_CLIENT_ID = os.getenv("SYNC_CLIENT_ID", "")
SYNC_CLIENT_SECRET = os.getenv("SYNC_CLIENT_SECRET", "")
SYNC_WEBHOOK_URL = os.getenv("SYNC_WEBHOOK_URL", "").strip()

    MEDIA = {
    "WELCOME_VIDEO": "https://res.cloudinary.com/declnidxc/video/upload/v1770453000/lv_0_20260128120445_ltxyrw.mp4",
    "DATA_VIDEO": "https://res.cloudinary.com/declnidxc/video/upload/v1770454441/lv_0_20260207055140_obfflt.mp4",
    "PAYMENT_VIDEO": "https://res.cloudinary.com/declnidxc/video/upload/v1770454441/lv_0_20260207055140_obfflt.mp4",
    "REMINDER_VIDEO": "https://res.cloudinary.com/declnidxc/video/upload/v1776976877/lv_0_20260423173934_rzcqdg.mp4"
}
}

user_states = {}
user_data = {}
pending_orders = {}
order_counter = 1

_token_cache = {
    "access_token": None,
    "expires_at": 0
}


def menu():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📅 Plano Mensal", callback_data="mensal"))
    kb.add(InlineKeyboardButton("💎 Plano Vitalício", callback_data="vitalicio"))
    kb.add(InlineKeyboardButton("🆘 Suporte", url=SUPORTE_LINK))
    return kb


def payment_actions():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Já paguei (verificar)", url=SUPORTE_LINK))
    kb.add(InlineKeyboardButton("🆘 Suporte", url=SUPORTE_LINK))
    return kb


def fetch_file_from_url(url: str):
    if not url:
        return None

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    file_data = BytesIO(response.content)
    return file_data


def send_video_from_url(chat_id: int, url: str, caption: str = None):
    try:
        if not url:
            return

        file_data = fetch_file_from_url(url)
        if not file_data:
            return

        file_data.name = "video.mp4"
        bot.send_video(chat_id, file_data, caption=caption)
    except Exception as e:
        print("Erro ao enviar vídeo:", e)


def get_plan_amount(plan):
    if plan == "mensal":
        return 29.90
    elif plan == "vitalicio":
        return 97.00
    return 0.0


def get_plan_name(plan):
    if plan == "mensal":
        return "Plano Mensal"
    elif plan == "vitalicio":
        return "Plano Vitalício"
    return "Plano"


def get_sync_token():
    now = time.time()

    if _token_cache["access_token"] and now < _token_cache["expires_at"] - 30:
        return _token_cache["access_token"]

    url = f"{SYNC_BASE_URL}/api/partner/v1/auth-token"
    payload = {
        "client_id": SYNC_CLIENT_ID,
        "client_secret": SYNC_CLIENT_SECRET
    }

    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()

    data = response.json()
    access_token = data["access_token"]
    expires_in = int(data.get("expires_in", 3600))

    _token_cache["access_token"] = access_token
    _token_cache["expires_at"] = now + expires_in

    return access_token


def create_pix_payment(amount, description, client_name, cpf, email, phone):
    token = get_sync_token()

    url = f"{SYNC_BASE_URL}/api/partner/v1/cash-in"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = {
        "amount": amount,
        "description": description,
        "client": {
            "name": client_name,
            "cpf": cpf,
            "email": email,
            "phone": phone
        }
    }

    if SYNC_WEBHOOK_URL:
        payload["webhook_url"] = SYNC_WEBHOOK_URL

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()

    return response.json()


def reminder_after_delay(chat_id: int, user_id: int, minutes: int = 5):
    try:
        time.sleep(minutes * 60)

        order = pending_orders.get(user_id)
        if not order:
            return

        if order.get("status") != "pending":
            return

        bot.send_message(
            chat_id,
            "⏳ *Seu pagamento ainda está pendente.*\n\n"
            "Se já iniciou, finalize agora para não perder sua condição especial."
        )

        send_video_from_url(
            chat_id,
            MEDIA["REMINDER_VIDEO"],
            "⚡ *Falta só concluir o pagamento para entrar no VIP.*"
        )

        bot.send_message(
            chat_id,
            "Depois de pagar, clique em *Já paguei (verificar)* 👇",
            reply_markup=payment_actions()
        )
    except Exception as e:
        print("Erro no lembrete automático:", e)


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "🔥 *Bem-vindo ao BrasilPrime VIP* 🔥\n\n"
        "Aqui você entra em um ambiente *EXCLUSIVO* que poucos têm acesso.\n\n"
        "*Ao entrar, você desbloqueia:*\n"
        "✨ Conteúdos premium e privados\n"
        "🔥 Atualizações frequentes\n"
        "🎥 Conteúdos raros\n"
        "💎 Acesso VIP\n\n"
        "⚠️ *Aviso:* vagas limitadas para manter a qualidade do grupo.\n\n"
        "👇 Escolha seu plano abaixo:",
        reply_markup=menu()
    )

    send_video_from_url(
        message.chat.id,
        MEDIA["WELCOME_VIDEO"],
        "🎥 *Olha o nível do que te espera no VIP...*"
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
            "Perfeito pra começar agora e ter acesso imediato ao VIP.\n\n"
            "✅ Acesso completo ao grupo\n"
            "✅ Conteúdos exclusivos\n"
            "✅ Suporte direto\n\n"
            "💰 *De R$ 59,90 por apenas R$ 29,90*\n\n"
            "⚠️ Promoção válida hoje",
            reply_markup=kb
        )

    elif call.data == "vitalicio":
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("💎 Assinar Vitalício", callback_data="pagar_vitalicio"))
        kb.add(InlineKeyboardButton("⬅️ Voltar", callback_data="voltar"))

        bot.send_message(
            call.message.chat.id,
            "💎 *Plano Vitalício*\n\n"
            "Entre uma vez e aproveite *pra sempre*.\n\n"
            "✅ Acesso permanente\n"
            "💎 Conteúdo premium liberado\n"
            "💎 Sem mensalidade\n"
            "💎 Melhor custo-benefício\n\n"
            "🔥 *Oferta especial:*\n"
            "De *R$ 197,00* por apenas *R$ 97,00*\n\n"
            "⚠️ Últimas vagas nesse valor",
            reply_markup=kb
        )

    elif call.data == "voltar":
        bot.send_message(
            call.message.chat.id,
            "📌 Escolha seu plano:",
            reply_markup=menu()
        )

    elif call.data == "pagar_mensal":
        user_states[call.from_user.id] = "cpf"
        user_data[call.from_user.id] = {"plano": "mensal"}

        bot.send_message(
            call.message.chat.id,
            "🔐 *Para continuar, precisamos de alguns dados.*\n\n"
            "Digite seu *CPF*:"
        )

        if MEDIA["DATA_VIDEO"]:
            send_video_from_url(
                call.message.chat.id,
                MEDIA["DATA_VIDEO"],
                "🔐 *Seus dados são usados somente para validar seu acesso.*"
            )

    elif call.data == "pagar_vitalicio":
        user_states[call.from_user.id] = "cpf"
        user_data[call.from_user.id] = {"plano": "vitalicio"}

        bot.send_message(
            call.message.chat.id,
            "🔐 *Para continuar, precisamos de alguns dados.*\n\n"
            "Digite seu *CPF*:"
        )

        if MEDIA["DATA_VIDEO"]:
            send_video_from_url(
                call.message.chat.id,
                MEDIA["DATA_VIDEO"],
                "🔐 *Processo seguro. Pode continuar tranquilo.*"
            )


@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    global order_counter

    user_id = message.from_user.id

    if user_id not in user_states:
        return

    state = user_states[user_id]

    if state == "cpf":
        user_data[user_id]["cpf"] = message.text.strip()
        user_states[user_id] = "telefone"

        bot.send_message(
            message.chat.id,
            "📱 Agora digite seu *telefone com DDD*:"
        )

    elif state == "telefone":
        tel = message.text.strip()

        if not tel.startswith("55"):
            tel = "55" + tel

        user_data[user_id]["telefone"] = tel
        user_states[user_id] = "email"

        bot.send_message(
            message.chat.id,
            "📧 Agora digite seu *email*:"
        )

    elif state == "email":
        user_data[user_id]["email"] = message.text.strip()
        user_states[user_id] = "finalizado"

        dados = user_data[user_id]
        plano = dados["plano"]
        amount = get_plan_amount(plano)
        plan_name = get_plan_name(plano)

        try:
            payment = create_pix_payment(
                amount=amount,
                description=plan_name,
                client_name=message.from_user.first_name or "Cliente",
                cpf=dados["cpf"],
                email=dados["email"],
                phone=dados["telefone"]
            )

            pix_code = payment.get("pix_code", "")
            identifier = payment.get("identifier", "")

            pending_orders[user_id] = {
                "status": "pending",
                "identifier": identifier,
                "pix_code": pix_code,
                "plan_name": plan_name
            }

            bot.send_message(
                message.chat.id,
                "✅ *Pagamento gerado com sucesso!*\n\n"
                f"📦 *Plano:* {plan_name}\n"
                f"💰 *Valor:* R$ {amount:.2f}\n"
                f"🧾 *Pedido:* #{order_counter}\n\n"
                f"📌 *Pix Copia e Cola:*\n`{pix_code}`\n\n"
                "Depois de pagar, clique abaixo 👇",
                reply_markup=payment_actions()
            )

            send_video_from_url(
                message.chat.id,
                MEDIA["PAYMENT_VIDEO"],
                "⚡ *Falta só concluir o pagamento para liberar seu acesso.*"
            )

            threading.Thread(
                target=reminder_after_delay,
                args=(message.chat.id, user_id, 5),
                daemon=True
            ).start()

            order_counter += 1

        except Exception as e:
            bot.send_message(
                message.chat.id,
                f"❌ *Erro ao gerar pagamento:*\n`{str(e)}`"
            )
            print("Erro ao gerar pagamento:", e)


def run_bot():
    bot.infinity_polling(skip_pending=True)
