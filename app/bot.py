import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

# Controle de fluxo
user_states = {}
user_data = {}


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
        "💎 Aqui você desbloqueia acesso a um ambiente exclusivo 💎\n\n"
        "*Ao assinar, você recebe:*\n"
        "✨ Famosas do OnlyFans / Privacy\n"
        "🔥 Ninfetas +18 🇧🇷\n"
        "🕶️ Conteúdos ocultos +18\n"
        "🎥 Vídeos vazados raros\n"
        "💋 Sexo e conteúdos exclusivos\n\n"
        "📌 *Escolha abaixo o plano ideal para você:*",
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
            "Ideal para começar agora com acesso completo.\n\n"
            "✅ Conteúdos exclusivos\n"
            "✅ Acesso VIP\n"
            "✅ Suporte\n\n"
            "💰 *Hoje por apenas R$ 29,90*",
            reply_markup=kb
        )

    elif call.data == "vitalicio":
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("💎 Assinar Vitalício", callback_data="pagar_vitalicio"))
        kb.add(InlineKeyboardButton("⬅️ Voltar", callback_data="voltar"))

        bot.send_message(
            call.message.chat.id,
            "💎 *Plano Vitalício*\n\n"
            "A melhor escolha para acesso completo sem mensalidade.\n\n"
            "💎 Conteúdos premium\n"
            "💎 Acesso permanente\n"
            "💎 Suporte 24h\n\n"
            "🔥 *Oferta especial*\n"
            "De *R$ 197,00* por apenas *R$ 97,00*",
            reply_markup=kb
        )

    elif call.data == "voltar":
        bot.send_message(
            call.message.chat.id,
            "📌 *Escolha abaixo o plano ideal para você:*",
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

    elif call.data == "pagar_vitalicio":
        user_states[call.from_user.id] = "cpf"
        user_data[call.from_user.id] = {"plano": "vitalicio"}

        bot.send_message(
            call.message.chat.id,
            "🔐 *Para continuar, precisamos de alguns dados.*\n\n"
            "Digite seu *CPF*:"
        )


# 🔥 CAPTURA DE DADOS
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id

    if user_id not in user_states:
        return

    state = user_states[user_id]

    # CPF
    if state == "cpf":
        user_data[user_id]["cpf"] = message.text
        user_states[user_id] = "telefone"

        bot.send_message(
            message.chat.id,
            "📱 Agora digite seu *telefone com DDD*:"
        )

    # TELEFONE
    elif state == "telefone":
        user_data[user_id]["telefone"] = message.text
        user_states[user_id] = "email"

        bot.send_message(
            message.chat.id,
            "📧 Agora digite seu *e-mail*:"
        )

    # EMAIL
    elif state == "email":
        user_data[user_id]["email"] = message.text
        user_states[user_id] = "finalizado"

        dados = user_data[user_id]

        bot.send_message(
            message.chat.id,
            "✅ *Cadastro concluído!*\n\n"
            f"📄 CPF: {dados['cpf']}\n"
            f"📱 Telefone: {dados['telefone']}\n"
            f"📧 Email: {dados['email']}\n\n"
            "⚡ Agora vamos gerar seu pagamento..."
        )


def run_bot():
    bot.infinity_polling(skip_pending=True)
