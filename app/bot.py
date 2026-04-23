import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")


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
        "💎 Aqui você desbloqueia acesso a um ambiente exclusivo, que você  NÃO encontra FÁCIL 💎\n\n"
        "*Ao assinar, você recebe:*\n"
        "✨ Famosas do OnlyFans / Privacy ✅\n"
    "🔥 Ninfetas +18 🇧🇷 ✅\n"
    "🕶️ Conteúdos ocultos +18 (BRUTAL) ✅\n"
    "🎥 Vídeos vazados RAROS ✅\n"
    "🚫 Incest0s 🔞 ✅\n"
    "💋 Sexo, putaria e MUITO MAIS... ✅\n\n"
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
            "Ideal para quem quer começar agora com investimento baixo e acesso completo ao ambiente VIP.\n\n"
            "✅ Acesso ao grupo VIP\n"
            "✅ Conteúdos exclusivos\n"
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
            "A melhor escolha para quem quer entrar uma vez e aproveitar tudo sem mensalidade e sem renovação.\n\n"
            "✅ Acesso permanente ao VIP\n"
            "💎 Conteúdos Premium e exclusivos ✅\n"
            "💎 Suporte 24hrs ✅\n"
            "💎💸 Melhor custo-benefício ✅\n"
            "🔥 *Condição especial de hoje* ✅\n"
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
        bot.send_message(
            call.message.chat.id,
            "💳 *Plano Mensal selecionado.*\n\n"
            "Agora vamos iniciar seu cadastro para gerar o pagamento com segurança."
        )

    elif call.data == "pagar_vitalicio":
        bot.send_message(
            call.message.chat.id,
            "💎 *Plano Vitalício selecionado.*\n\n"
            "Excelente escolha. Agora vamos iniciar seu cadastro para gerar o pagamento com segurança."
        )


def run_bot():
    bot.infinity_polling(skip_pending=True)
