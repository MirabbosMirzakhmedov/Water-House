import logging
from datetime import datetime
import telebot as telebot
from telebot.types import CallbackQuery, ReplyKeyboardRemove

import config.secret as payload
import markups as m
from database import Database
from translations import _

bot: telebot.TeleBot = telebot.TeleBot(token=payload.BOT_TOKEN)
db = Database('../database/water_house.db')
user_history = {}
item = None


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

@bot.message_handler(
    func=lambda message: message.text == "💧 Вода"
    or message.text == "💧 Suv")
def water_button_handler(message):
    if message.chat.type == 'private':
        lang = db.get_lang(message.chat.id)
        bot.send_message(
            text=_('💧 Выберите тип воды:', lang),
            chat_id=message.chat.id,
            reply_markup=m.water_type_menu(db, lang)
        )
        user_history[message.chat.id].append(message.text)

@bot.message_handler(
    func=lambda message: message.text == "🚰 Кулер"
    or message.text == "🚰 Kuler")
def cooler_button_handler(message):
    if message.chat.type == 'private':
        lang = db.get_lang(message.chat.id)
        bot.send_message(
            text=_("🚰 Выберите кулер", lang),
            chat_id=message.chat.id,
            reply_markup=m.coolers_menu(db, lang)
        )
        user_history[message.chat.id].append(message.text)


@bot.message_handler(
    func=lambda message: message.text == "🌐 Выбрать язык"
    or message.text == "🌐 Tilni tanlash")
def choose_lang_handler(message):
    if message.chat.type == 'private':
        bot.send_message(message.chat.id,
            'Iltimos, tilni tanlang\n'
            'Пожалуйста, выберите язык 🔽',
            reply_markup=m.update_lang())


@bot.message_handler(func=lambda message: message.text.isdigit())
def handle_digit_input(message):
    global item
    # breakpoint()
    if message.chat.type == 'private':
        lang = db.get_lang(message.chat.id)
        number = int(message.text)
        try:

            date_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Determine the type of item (cooler or water) based on a condition
            if item[1] == 'cooler':
                subtotal = number * item[9]
                item = db.insert_cooler_order(
                    date_created=date_created,
                    cooler_id=item[0],
                    chat_id=message.chat.id,
                    quantity=number,
                    subtotal=subtotal
                )
            elif item[1] == 'water':
                subtotal = number * item[4]
                item = db.insert_water_order(
                    date_created=date_created,
                    water_id=item[0],
                    chat_id=message.chat.id,
                    quantity=number,
                    subtotal=subtotal
                )

            bot.send_message(
                chat_id=message.chat.id,
                text=f'{_("Отличный выбор, у вас есть 3 часа на завершение заказа, иначе он будет удален из корзины.", lang)}'
                     f'\n\n{_("Хотите добавить еще что-то?", lang)}',
                reply_markup=m.start_menu(message.chat.id, lang),
            )
        except Exception as e:
            print('The error message:', e)
            bot.send_message(message.chat.id,
                             _("Что-то пошло не так. Пожалуйста, повторите попытку позже.",
                               lang))


# @bot.message_handler(func=lambda message: message.text.isdigit())
# def cooler_is_digit(message):
#     global item
#     if message.chat.type == 'private':
#         lang = db.get_lang(message.chat.id)
#         number = int(message.text)
#         try:
#             subtotal = number * item[8]
#             date_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#             item = db.insert_cooler_order(
#                 date_created=date_created,
#                 cooler_id=item[0],
#                 chat_id=message.chat.id,
#                 quantity=number,
#                 subtotal=subtotal
#             )
#             bot.send_message(
#                 chat_id=message.chat.id,
#                 text=f'{_("Отличный выбор, у вас есть 3 часа на завершение заказа, иначе он будет удален из корзины.", lang)}'
#                      f'\n\n{_("Хотите добавить еще что-то?", lang)}',
#                 reply_markup=m.start_menu(message.chat.id, lang),
#             )
#         except:
#             bot.send_message(message.chat.id, _("Что-то пошло не так. Пожалуйста, повторите попытку позже.", lang))
#
# @bot.message_handler(func=lambda message: message.text.isdigit())
# def water_is_digit(message):
#     global item
#     if message.chat.type == 'private':
#         lang = db.get_lang(message.chat.id)
#         number = int(message.text)
#         try:
#
#             breakpoint()
#             subtotal = number * item[8]
#             date_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#             item = db.insert_water_order(
#                 date_created=date_created,
#                 water_id=item[0],
#                 chat_id=message.chat.id,
#                 quantity=number,
#                 subtotal=subtotal
#             )
#             bot.send_message(
#                 chat_id=message.chat.id,
#                 text=f'{_("Отличный выбор, у вас есть 3 часа на завершение заказа, иначе он будет удален из корзины.", lang)}'
#                      f'\n\n{_("Хотите добавить еще что-то?", lang)}',
#                 reply_markup=m.start_menu(message.chat.id, lang),
#             )
#         except Exception:
#             bot.send_message(message.chat.id,
#                              _("Что-то пошло не так. Пожалуйста, повторите попытку позже.",
#                                lang))


##########
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    global item
    if message.chat.type == 'private':
        lang = db.get_lang(message.chat.id)
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
        if water_order and message.text == water_order[0][2]:
            item = db.get_water_order(message.text)[0]
            product = {
                _('Названия', lang): item[2],
                _('Объем', lang): item[3],
                _('Цена', lang): item[4],
                _('Описание', lang): item[5],
            }

            photo = db.get_water_image(item[0])
            caption = f"" \
f"<b>{product[_('Названия', lang)]}, {product[_('Объем', lang)]}\n\n</b>" \
f"{product[_('Описание', lang)]}\n\n" \
f"{_('Доступно', lang)}: <b>{db.count_water(item[0])}</b> | " \
f"<b>{_('Цена', lang)}: {product[_('Цена', lang)]} UZS</b>\n\n" \
f"{_('Выберите количество', lang)}\n{_('Или напишите число, сколько вы хотите 🔽', lang)}"
            bot.send_photo(message.chat.id, photo=photo,
            caption=caption,
            parse_mode="HTML",
            reply_markup=m.water_amount(db,lang,item[0]))
            user_history[message.chat.id].append(message.text)


        # handle cooler order
        cooler_order = db.get_cooler_order(message.text)
        if cooler_order and message.text == cooler_order[0][2]:
            item = db.get_cooler_order(message.text)[0]
            product = {
                _('Названия', lang): item[2],
                _('Описание', lang): item[3],
                _('Тип', lang): item[4],
                _('Установка капсул воды', lang): item[5],
                _('Нагрев', lang): item[6],
                _('Глубина', lang): item[7],
                _('Высота', lang): item[8],
                _('Цена', lang): item[9],

            }
            photo = db.get_cooler_image(item[0])
            answer = _(product[_('Нагрев', lang)])
            caption = f"" \
f"<b>{product[_('Названия', lang)]}</b>\n\n" \
f"{product[_('Описание', lang)]}\n\n" \
f"<b>{_('Тип', lang)}:</b> {_(product[_('Тип', lang)], lang)}\n" \
f"<b>{_('Установка капсул воды', lang)}:</b> {_(product[_('Установка капсул воды', lang)], lang)}\n" \
f"<b>{_('Нагрев', lang)}:</b> {_(answer, lang)}\n" \
f"<b>{_('Глубина', lang)}:</b> {product[_('Глубина', lang)]} {_('см', lang)}\n" \
f"<b>{_('Высота', lang)}:</b> {product[_('Высота', lang)]} {_('см', lang)}\n\n" \
f"{_('Доступно', lang)}: <b>{db.count_cooler(item[0])}</b> | " \
f"<b>{_('Цена', lang)}: {product[_('Цена', lang)]} UZS</b>\n\n" \
f"{_('Выберите количество', lang)}\n{_('Или напишите число, сколько вы хотите 🔽', lang)}"

            bot.send_photo(message.chat.id, photo=photo,
                caption=caption,
                parse_mode="HTML",
                reply_markup=m.cooler_amount(db=db, lang=lang, id=item[0]))
            user_history[message.chat.id].append(message.text)
            return


@bot.message_handler(
    func=lambda message: message.text == "⬅️ Назад"
    or message.text == "⬅️ Ortga")
def back_button_handler(message):
    if message.chat.type == 'private':
        if user_history[message.chat.id]:
            lang = db.get_lang(message.chat.id)
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