import os
import telebot

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "✅ Bot pronto para pegar FILE_ID.\n\n"
        "Agora envie o vídeo aqui neste chat."
    )


@bot.message_handler(content_types=[
    "video",
    "document",
    "animation",
    "photo",
    "audio",
    "voice",
    "video_note"
])
def pegar_file_id(message):

    if message.video:
        file_id = message.video.file_id
        tipo = "VIDEO"

    elif message.document:
        file_id = message.document.file_id
        tipo = "DOCUMENTO"

    elif message.animation:
        file_id = message.animation.file_id
        tipo = "ANIMATION/GIF"

    elif message.photo:
        file_id = message.photo[-1].file_id
        tipo = "FOTO"

    elif message.audio:
        file_id = message.audio.file_id
        tipo = "AUDIO"

    elif message.voice:
        file_id = message.voice.file_id
        tipo = "VOICE"

    elif message.video_note:
        file_id = message.video_note.file_id
        tipo = "VIDEO_NOTE"

    else:
        bot.send_message(message.chat.id, "❌ Não consegui identificar o arquivo.")
        return

    bot.send_message(
        message.chat.id,
        f"📌 *FILE_ID encontrado!*\n\n"
        f"*Tipo:* {tipo}\n\n"
        f"`{file_id}`"
    )

    print(f"FILE_ID {tipo}: {file_id}")


@bot.message_handler(func=lambda message: True)
def fallback(message):
    bot.send_message(
        message.chat.id,
        "⚠️ Envie um vídeo, imagem ou arquivo para eu pegar o FILE_ID."
    )


def run_bot():
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)


if __name__ == "__main__":
    run_bot()
