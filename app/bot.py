import os
from io import BytesIO
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

SUPORTE_LINK = "https://t.me/anonimoprimevip"

# ===== SEUS VÍDEOS =====
MEDIA = {
    "WELCOME_VIDEO": "https://res.cloudinary.com/declnidxc/video/upload/v1770453000/lv_0_20260128120445_ltxyrw.mp4",
    "DATA_VIDEO": "https://res.cloudinary.com/declnidxc/video/upload/v1770453009/https:/res.cloudinary.com/lv_0_20260207052358/video/upload/v123456/video.mp4",
    "PAYMENT_VIDEO": "https://res.cloudinary.com/declnidxc/video/upload/v1770454441/lv_0_20260207055140_obfflt.mp4",
}

# ===== CONTROLE =====
user_states = {}
user_data = {}


def menu():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📅 Plano Mensal", callback_data="mensal"))
    kb.add(InlineKeyboardButton("💎 Plano Vitalício", callback_data="vitalicio"))
    kb.add(InlineKeyboardButton("🆘 Suporte", url=SUPORTE_LINK))
    return kb


def support_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Já paguei (verificar)", url=SUPORTE_LINK))
    kb.add(InlineKeyboardButton("🆘 Suporte", url=SUPORTE_LINK))
    return kb


def send_video(chat_id, url, caption=None):
    try:
        if "COLE_AQUI" in url:
            return

        r = requests.get(url)
        video = BytesIO(r.content)
        video.name = "video.mp4"

        bot.send_video(chat_id, video, caption=caption)
    except Exception as e:
        print("Erro vídeo:", e)


# ===== START =====
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "🔥 *Bem-vindo ao BrasilPrime VIP* 🔥\n\n"
        "Ambiente exclusivo + conteúdos que você NÃO encontra fácil.\n\n"
        "⚠️ Vagas limitadas\n\n"
        "👇 Escolha seu plano:",
        reply_markup=menu()
    )

    send_video(
        message.chat.id,
        MEDIA["WELCOME_VIDEO"],
        "🎥 *Olha o nível do que te espera no VIP...*"
    )


# ===== CALLBACKS =====
@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):

    if call.data == "mensal":
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("💳 Assinar Mensal", callback_data="pagar_mensal"))
        kb.add(InlineKeyboardButton("⬅️ Voltar", callback_data="voltar"))

        bot.send_message(
            call.message.chat.id,
            "📅 *Plano Mensal*\n\n"
            "💰 De R$ 59,90 por apenas *R$ 29,90*\n\n"
            "⚠️ Promoção hoje",
            reply_markup=kb
        )

    elif call.data == "vitalicio":
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("💎 Assinar Vitalício", callback_data="pagar_vitalicio"))
        kb.add(InlineKeyboardButton("⬅️ Voltar", callback_data="voltar"))

        bot.send_message(
            call.message.chat.id,
            "💎 *Plano Vitalício*\n\n"
            "🔥 Melhor escolha\n\n"
            "De *R$ 197* por apenas *R$ 97*",
            reply_markup=kb
        )

    elif call.data == "voltar":
        bot.send_message(call.message.chat.id, "Escolha um plano:", reply_markup=menu())

    elif call.data == "pagar_mensal":
        user_states[call.from_user.id] = "cpf"
        user_data[call.from_user.id] = {"plano": "mensal"}

        bot.send_message(call.message.chat.id, "Digite seu *CPF*:")

        send_video(
            call.message.chat.id,
            MEDIA["DATA_VIDEO"],
            "🔐 *Seus dados são protegidos e usados apenas para validação.*"
        )

    elif call.data == "pagar_vitalicio":
        user_states[call.from_user.id] = "cpf"
        user_data[call.from_user.id] = {"plano": "vitalicio"}

        bot.send_message(call.message.chat.id, "Digite seu *CPF*:")

        send_video(
            call.message.chat.id,
            MEDIA["DATA_VIDEO"],
            "🔐 *Processo seguro. Pode continuar tranquilo.*"
        )


# ===== CAPTURA =====
@bot.message_handler(func=lambda message: True)
def handle(message):
    uid = message.from_user.id

    if uid not in user_states:
        return

    state = user_states[uid]

    if state == "cpf":
        user_data[uid]["cpf"] = message.text
        user_states[uid] = "telefone"
        bot.send_message(message.chat.id, "Digite seu *telefone com DDD*:")

    elif state == "telefone":
        tel = message.text

        if not tel.startswith("55"):
            tel = "55" + tel

        user_data[uid]["telefone"] = tel
        user_states[uid] = "email"
        bot.send_message(message.chat.id, "Digite seu *email*:")

    elif state == "email":
        user_data[uid]["email"] = message.text
        user_states[uid] = "finalizado"

        bot.send_message(
            message.chat.id,
            "💳 *Pagamento gerado*\n\n"
            "Finalize para liberar seu acesso.\n\n"
            "Depois clique abaixo 👇",
            reply_markup=support_kb()
        )

        send_video(
            message.chat.id,
            MEDIA["PAYMENT_VIDEO"],
            "⚡ *Falta só concluir o pagamento para entrar no VIP.*"
        )


def run_bot():
    bot.infinity_polling(skip_pending=True)
