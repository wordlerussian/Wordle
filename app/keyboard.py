from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardButton,InlineKeyboardMarkup

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Настройки ⚙️")]
],resize_keyboard=True,input_field_placeholder="Давайте же начнем !")

main2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Играть 🕹",callback_data="start_play")]
])

main3 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Настройки ⚙️",callback_data="settings")]
])

main4 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Да, поставить 6 жизней ✅",callback_data="turn_off_inf")],
    [InlineKeyboardButton(text="Нет, оставить бесконечность ❌",callback_data="nothing")]
])

main5 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Да, поставить бесконечность ✅",callback_data="turn_on_inf")],
    [InlineKeyboardButton(text="Нет, оставить 6 жизней ❌",callback_data="nothing")]
])

main6 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Выйти из игры 🚪",callback_data="quit")]
])

main7 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Да ✅", callback_data="settings_yes"),InlineKeyboardButton(text="Нет ❌",callback_data="nothing")]
]) 