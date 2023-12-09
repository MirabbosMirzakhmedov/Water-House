from telebot.types import (
    ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from translations import _

def start_menu(chat_id, lang):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = KeyboardButton(_('💧 Вода', lang))
    item2 = KeyboardButton(_('🚰 Кулер', lang))
    item3 = KeyboardButton(_("🌐 Выбрать язык", lang))
    markup.add(item1, item2)
    markup.add(item3)
    return markup

def lang_menu():
    lang_menu = InlineKeyboardMarkup(row_width=2)
    lang_uz = InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data='lang_uz')
    lang_ru = InlineKeyboardButton(text="🇷🇺 Русский", callback_data='lang_ru')
    lang_menu.add(lang_uz, lang_ru)
    return lang_menu

def update_lang():
    lang_menu = InlineKeyboardMarkup(row_width=2)
    lang_uz = InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data='update_lang_uz')
    lang_ru = InlineKeyboardButton(text="🇷🇺 Русский", callback_data='update_lang_ru')
    lang_menu.add(lang_uz, lang_ru)



    return lang_menu

def water_type_menu(db, lang):
    products = db.get_products()  # Assuming each product is a tuple with (product_name,)

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    row_buttons = []

    for product in products:
        # Use the translation if available, otherwise use the original text
        translated_product_name = _(product[0], lang)
        button = KeyboardButton(translated_product_name)
        row_buttons.append(button)

        if len(row_buttons) == 2:
            markup.add(*row_buttons)
            row_buttons = []

    if len(row_buttons) == 1:
        markup.add(row_buttons[0])

    # Translate the "⬅️ Back" button
    translated_back_text = _("⬅️ Назад", lang)
    back = KeyboardButton(translated_back_text)
    markup.add(back)

    return markup

def coolers_menu(db, lang):
    coolers = db.get_coolers()
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    row_buttons = []

    for cooler in coolers:
        # Use the translation if available, otherwise use the original text
        translated_cooler_name = _(cooler[0], lang)
        button = KeyboardButton(translated_cooler_name)
        row_buttons.append(button)

        if len(row_buttons) == 2:
            markup.add(*row_buttons)
            row_buttons = []

    if len(row_buttons) == 1:
        markup.add(row_buttons[0])

        # Translate the "⬅️ Back" button
    translated_back_text = _("⬅️ Назад", lang)
    back = KeyboardButton(text=translated_back_text)
    markup.add(back)

    return markup

def get_water(db, lang, product_id):
    water_bottles = db.get_water(product_id)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    row_buttons = []

    for item in water_bottles:
        # Use the translation if available, otherwise use the original text
        translated_product_name = _(item[0], lang)
        button = KeyboardButton(translated_product_name)
        row_buttons.append(button)

        if len(row_buttons) == 2:
            markup.add(*row_buttons)
            row_buttons = []

    if len(row_buttons) == 1:
        markup.add(row_buttons[0])

    # Translate the "⬅️ Back" button
    translated_back_text = _("⬅️ Назад", lang)
    back = KeyboardButton(text=translated_back_text)
    markup.add(back)

    return markup

