import logging

import telebot as telebot
from telebot.types import CallbackQuery, ReplyKeyboardRemove

import config.secret as payload
import markups as m
from database import Database
from translations import _

bot: telebot.TeleBot = telebot.TeleBot(token=payload.BOT_TOKEN)
db = Database('../database/water_house.db')
user_history = {}

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type == 'private':
        if not db.user_exists(message.chat.id):
            bot.send_message(message.chat.id, 'Iltimos, tilni tanlang\n'
                                              'Пожалуйста, выберите язык 🔽',
                             reply_markup=m.lang_menu())
        else:
            lang = db.get_lang(message.chat.id)
            # button is not disappearing
            bot.send_message(
                message.chat.id,
                text=_('😊 Что вас интересует?', lang),
                reply_markup=m.start_menu(message.chat.id, lang)
            )
            user_id = message.from_user.id
            user_history[user_id] = []


# команда для рассылки
@bot.message_handler(commands=['sendall'])
def sendall(message):
    if message.chat.type == 'private':
        if message.chat.id == 368195441:
            lang = db.get_lang(message.chat.id)
            text = message.text[9:]
            users = db.get_users()
            for row in users:
                try:
                    bot.send_message(chat_id=row[0], text=text)
                    if int(row[1]) != 1:
                        db.set_active(chat_id=row[0], active=1)
                except:
                    db.set_active(chat_id=row[0], active=0)
            bot.send_message(message.chat.id, _('Успешная рассылка!', lang))

#@bot.callback_query_handler(func=lambda callback: callback.data)
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('lang_'))
def set_language(callback: CallbackQuery):
    bot.delete_message(callback.from_user.id, callback.message.message_id)
    if not db.user_exists(callback.from_user.id):
        lang = callback.data[5:]
        db.add_user(callback.from_user.id, lang=lang)

        bot.send_message(
            callback.from_user.id,
            text=_('😊 Что вас интересует?', lang),
            reply_markup=m.start_menu(callback.from_user.id,lang)
        )

@bot.callback_query_handler(func=lambda callback: callback.data.startswith('update_lang_'))
def update_language(callback: CallbackQuery):
    lang = callback.data[12:]
    db.update_lang(lang, callback.from_user.id)
    bot.delete_message(callback.from_user.id, callback.message.message_id)
    bot.send_message(
        callback.from_user.id,
        text=_('😊 Что вас интересует?', lang),
        reply_markup=m.start_menu(callback.from_user.id, lang)
    )

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.chat.type == 'private':
        lang = db.get_lang(message.chat.id)

        # button to change language
        if message.text == _("🌐 Выбрать язык", lang):
            bot.send_message(message.chat.id,
'Iltimos, tilni tanlang\n'
'Пожалуйста, выберите язык 🔽',
            reply_markup=m.update_lang())

        # Suv handler
        if message.text == "💧 Вода" or message.text == "💧 Suv":
            bot.send_message(
                text=_('💧 Выберите тип воды:', lang),
                chat_id=message.chat.id,
                reply_markup=m.water_type_menu(db, lang)
            )
            user_history[message.chat.id].append(message.text)

        if message.text == "🚰 Кулер" or message.text == "🚰 Kuler":
            bot.send_message(
                text=_("🚰 Выберите кулер", lang),
                chat_id=message.chat.id,
                reply_markup=m.coolers_menu(db, lang)
            )
            user_history[message.chat.id].append(message.text)

        # handle water type (gazli, gazsiz, etc)
        products = db.get_products()
        matching_product = next((item for item in products if message.text in item), None)
        if matching_product:
            water_text = matching_product[1]
            product_id = db.get_product_id(water_text)
            bot.send_message(
                text=_("💧 Выберите воду", lang),
                chat_id=message.chat.id,
                reply_markup=m.get_water(db, lang, product_id)
            )
            user_history[message.chat.id].append(message.text)

        # handler for water products
        water_order = db.get_water_order(message.text)
        if water_order and message.text == water_order[0][1]:
            item = db.get_water_order(message.text)[0]
            product = {
                _('Названия', lang): item[1],
                _('Объем', lang): item[2],
                _('Цена', lang): item[3],
                _('Описание', lang): item[4],
            }
            photo = db.get_water_image(item[0])
            caption = f"" \
f"<b>{product[_('Названия', lang)]}, {product[_('Объем', lang)]}\n\n</b>" \
f"{product[_('Описание', lang)]}\n\n" \
f"<b>{_('Цена', lang)}: {product[_('Цена', lang)]} UZS</b>"
            bot.send_photo(message.chat.id, photo=photo,
            caption=caption,
            parse_mode="HTML")
            user_history[message.chat.id].append(message.text)

        # handle cooler order
        cooler_order = db.get_cooler_order(message.text)
        if cooler_order and message.text == cooler_order[0][1]:
            item = db.get_cooler_order(message.text)[0]
            product = {
                _('Названия', lang): item[1],
                _('Описание', lang): item[2],
                _('Тип', lang): item[3],
                _('Установка капсул воды', lang): item[4],
                _('Нагрев', lang): item[5],
                _('Глубина', lang): item[6],
                _('Высота', lang): item[7],
                _('Цена', lang): item[8],

            }
            photo = db.get_cooler_image(item[0])
            answer = _(product[_('Нагрев', lang)])
            caption = f"" \
f"<b>{product[_('Названия', lang)]}</b>\n\n" \
f"{product[_('Описание', lang)]}\n\n" \
f"<b>{_('Тип', lang)}:</b> {_(product[_('Тип', lang)], lang)}\n" \
f"<b>{_('Установка капсул воды', lang)}:</b> {_(product[_('Установка капсул воды', lang)], lang)}\n" \
f"<b>{_('Нагрев', lang)}:</b> {_(answer, lang)}\n" \
f"<b>{_('Глубина', lang)}:</b> {product[_('Глубина', lang)]}\n" \
f"<b>{_('Высота', lang)}:</b> {product[_('Высота', lang)]}\n\n" \
f"<b>{_('Цена', lang)}: {product[_('Цена', lang)]} UZS</b>"
            bot.send_photo(message.chat.id, photo=photo,
                           caption=caption,
                           parse_mode="HTML")
            user_history[message.chat.id].append(message.text)

        elif message.text == "⬅️ Назад" or message.text == "⬅️ Ortga":
            # breakpoint()
            if user_history[message.chat.id]:
                user_history[message.chat.id].pop()
                bot.send_message(
                    message.chat.id,
                    text=_('😊 Что вас интересует?', lang),
                    reply_markup=m.start_menu(message.chat.id, lang)
                )
                user_history[message.chat.id].append(message.text)













try:
    print('Bot is running')
    bot.infinity_polling(
        skip_pending=False,
        logger_level=logging.ERROR,
        allowed_updates=None,
        restart_on_change=False,
        path_to_watch=None
    )
except KeyboardInterrupt:
    bot.stop_polling()
    print('Bot stopped')