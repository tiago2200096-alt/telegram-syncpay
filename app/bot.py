import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.syncpay import create_pix_payment

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

user_states = {}
user_data = {}
order_counter = 1


def menu():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📅 Plano Mensal", callback_data="mensal"))
    kb.add(InlineKeyboardButton("💎 Plano Vitalício", callback_data="vitalicio"))
    kb.add(InlineKeyboardButton("🆘 Suporte", url="https://t.me/anonimoprimevip"))
    return kb


def payment_actions():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Já paguei", callback_data="ja_paguei"))
    kb.add(InlineKeyboardButton("🆘 Suporte", url="https://t.me/anonimoprimevip"))
    return kb


def get_plan_amount(plan):
    if plan == "mensal":
        return 29.90
    elif plan == "vitalicio":
        return 97.00
    return 0


def get_plan_name(plan):
    if plan == "mensal":
        return "Plano Mensal"
    elif plan == "vitalicio":
        return "Plano Vitalício"
    return "Plano"


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
    global order_counter

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

    elif call.data == "ja_paguei":
        bot.send_message(
            call.message.chat.id,
            "✅ *Pagamento informado.*\n\n"
            "Se o Pix já foi concluído, clique em *Suporte* e envie seu número de pedido para agilizar a liberação."
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
        user_data[user_id]["telefone"] = message.text.strip()
        user_states[user_id] = "email"

        bot.send_message(
            message.chat.id,
            "📧 Agora digite seu *e-mail*:"
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

            dados["order_id"] = order_counter
            dados["pix_code"] = pix_code
            dados["identifier"] = identifier

            bot.send_message(
                message.chat.id,
                "✅ *Cadastro concluído e pagamento gerado!*\n\n"
                f"🧾 *Pedido:* #{order_counter}\n"
                f"📦 *Plano:* {plan_name}\n"
                f"💰 *Valor:* R$ {amount:.2f}\n\n"
                f"📌 *Pix Copia e Cola:*\n`{pix_code}`\n\n"
                "Depois de pagar, clique em *Já paguei* ou fale com o *Suporte*.",
                reply_markup=payment_actions()
            )

            order_counter += 1

        except Exception as e:
            bot.send_message(
                message.chat.id,
                "❌ *Não consegui gerar seu pagamento agora.*\n\n"
                "Fale com o suporte para finalizar manualmente."
            )
            print("Erro ao gerar pagamento:", e)


def run_bot():
    bot.infinity_polling(skip_pending=True)
