from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Plano Mensal", callback_data="mensal")],
            [InlineKeyboardButton(text="Plano Anual", callback_data="anual")],
            [InlineKeyboardButton(text="Suporte", url="https://t.me/seuusuario")]
        ]
    )
