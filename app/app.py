import logging, os, time
from datetime import datetime

import telebot as telebot
from openpyxl import Workbook
from telebot.types import CallbackQuery

import config.secret as payload
import markups as m
from database import Database
from translations import _

bot: telebot.TeleBot = telebot.TeleBot(token=payload.BOT_TOKEN)
db = Database('../database/water_house.db')
user_history = {}
item = ()


@bot.message_handler(commands=['admin'])
def admin(message):
    if message.chat.type == 'private':
        for admin in db.get_admins():
            if message.chat.id == admin[0]:
                lang = db.get_lang(message.chat.id)
                bot.send_message(
                    chat_id=message.chat.id,
                    text=f"""
{_('Список кнопок', lang)}:\n
/start - {_('Запустить бота', lang)}
/setadmin - {_('Назначить администратора', lang)}
/sendall - {_('Отправить рассылку', lang)}
/excel - {_('Загрузить отчет', lang)}
""")

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type == 'private':
        if not db.user_exists(message.chat.id):
            bot.send_message(message.chat.id, 'Iltimos, tilni tanlang\n'
                                              'Пожалуйста, выберите язык 🔽',
                             reply_markup=m.lang_menu())
            user_id = message.from_user.id
            user_history[user_id] = []
        else:
            lang = db.get_lang(message.chat.id)
            bot.send_message(
                message.chat.id,
                text=_('😊 Что вас интересует?', lang),
                reply_markup=m.start_menu(message.chat.id, lang)
            )
            user_id = message.from_user.id
            user_history[user_id] = []

@bot.message_handler(commands=['setadmin'])
def setadmin(message):
    if message.chat.type == 'private':
        for admin in db.get_admins():
            if message.chat.id == admin[0]:
                lang = db.get_lang(message.chat.id)
                new_admin_id = message.text[10:]
                if len(new_admin_id) == 0:
                    bot.send_message(
                        chat_id=message.chat.id,
                        text=_('Пожалуйста, присылайте в этом формате: /setadmin XXXXXXXX', lang)
                    )
                elif len(new_admin_id) > 1:
                    try:
                        admin_id_int = int(new_admin_id)
                        for admin in db.get_admins():
                            if admin_id_int == admin[0]:
                                db.set_admin(chat_id=admin_id_int)
                                bot.send_message(
                                    chat_id=message.chat.id,
                                    text=_('Вы успешно установили администратора', lang)
                                )
                                return
                        else:
                            bot.send_message(
                                chat_id=message.chat.id,
                                text=_('Неверный формат ID', lang)
                            )
                    except ValueError:
                        bot.send_message(
                            chat_id=message.chat.id,
                            text=_('Неверный формат ID', lang)
                        )
                    except Exception:
                        bot.send_message(
                            chat_id=message.chat.id,
                            text=_('Пожалуйста, присылайте в этом формате: /setadmin XXXXXXXX', lang)
                        )
                else:
                    bot.send_message(
                        chat_id=message.chat.id,
                        text=_(
                            'Пожалуйста, присылайте в этом формате: /setadmin XXXXXXXX',
                            lang)
                    )

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

@bot.message_handler(commands=['excel'])
def send_file(message):
    if message.chat.type == 'private':
        admins = db.get_admins()
        if any(chat_id[0] == message.chat.id for chat_id in admins):
            lang = db.get_lang(message.chat.id)
            today = str(datetime.today())
            file_path = f'C:/projects/Water House/report_{today[:10]}.xlsx'

            if os.path.exists(file_path):
                with open(file_path, 'rb') as file:
                    bot.send_document(chat_id=message.chat.id, document=file,
                        caption=_("Ваш отчет готов ✅", lang))
            else:
                orders = db.generate_excel()
                workbook = Workbook()
                sheet = workbook.active

                header = ['id', 'id_def', 'name', 'volume', 'price', 'definition', 'product_id', 'quantity']
                sheet.append(header)

                for order in orders:
                    sheet.append(order)

                workbook.save(file_path)
                workbook.close()

                with open(file_path, 'rb') as file:
                    bot.send_document(message.chat.id, file)


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
        user_history[callback.from_user.id].append(callback.data)

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
    user_history[callback.from_user.id].append(callback.data)

@bot.message_handler(
    func=lambda message: message.text == "💧 Вода"
    or message.text == "💧 Suv")
def water_button_handler(message):
    if message.chat.type == 'private':
        lang = db.get_lang(message.chat.id)
        bot.send_message(
            text=_('💧 Выберите тип воды', lang),
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
        user_history[message.chat.id].append(message.text)

@bot.message_handler(
    func=lambda message: message.text == "🔄 Очистить корзину"
    or message.text == "🔄 Savatni tozalash")
def empty_basket(message):
    global item
    if message.chat.type == 'private':
        lang = db.get_lang(message.chat.id)
        try:

            for item_q in [db.get_cooler_id(message.chat.id),
                           db.get_water_id(message.chat.id)]:
                if item_q and len(item_q) > 1:
                    if len(item_q) == 2:
                        if item_q == db.get_cooler_id(message.chat.id):
                            db.update_cooler_stock(quantity=item_q[1],
                                                   chat_id=message.chat.id)
                        elif item_q == db.get_water_id(message.chat.id):
                            db.update_water_stock(quantity=item_q[1],
                                                  chat_id=message.chat.id)
                    else:
                        bot.send_message(
                            message.chat.id,
                            text=_("Что-то произошло не так", lang))

            basket_items = db.get_basket(message.chat.id)
            if basket_items:
                db.empty_basket(message.chat.id)
                bot.send_message(
                    message.chat.id, _("Ваша корзинка теперь пуста", lang),
                    reply_markup=m.start_menu(message.chat.id, lang)
                )
                user_history[message.chat.id].append(message.text)
            else:
                bot.send_message(
                    message.chat.id, text=_("Ваша корзина пока пуста", lang))
                user_history[message.chat.id].append(message.text)

        except Exception as e:
            bot.send_message(
                message.chat.id, text=_("Что-то произошло не так", lang))

@bot.message_handler(
    func=lambda message: message.text == "📥 Корзинка"
    or message.text == "📥 Savat")
def see_basket(message):
    if message.chat.type == 'private':
        lang = db.get_lang(message.chat.id)
        basket = db.see_basket(message.chat.id)

        message_to_user = f"<b>{_('Ваша корзина', lang)}:</b>\n\n"
        total_price = 0

        try:
            for i, item in enumerate(basket, start=1):
                try:
                    product_name = item[2]
                    quantity = item[5]
                    price = item[6]

                    total_item_price = quantity * price
                    total_price += total_item_price

                    message_to_user += f"<b>{i}. {product_name}</b>\n"
                    message_to_user += f"{quantity} x {price:,} UZS = <b>{total_item_price:,} UZS</b>\n\n"
                except:
                    pass

            message_to_user += f"<b>{_('Общая стоимость', lang)}: {total_price:,} UZS</b>"
            bot.send_message(message.chat.id, text=message_to_user,
                 parse_mode='HTML', reply_markup=m.empty_basket(lang))
            user_history[message.chat.id].append(message.text)
        except:
            bot.send_message(message.chat.id, text=_("Ваша корзина пока пуста", lang))
            user_history[message.chat.id].append(message.text)

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

@bot.message_handler(
    func=lambda message: message.text == '🚚 Оформить заказ'
    or message.text == "🚚 Buyurtma berish")
def get_delivery_buttons(message):
    if message.chat.type == 'private':
        lang = db.get_lang(message.chat.id)

        bot.send_message(
            message.chat.id,
            text=_("Выберите тип доставки 👇🏻", lang),
            reply_markup=m.order_process_first(db, lang)
        )
        user_history[message.chat.id].append(message.text)


@bot.message_handler(func=lambda message: message.text.isdigit())
def handle_digit_input(message):
    global item
    if message.chat.type == 'private':
        lang = db.get_lang(message.chat.id)
        number = int(message.text)
        try:
            date_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if item[1] == 'cooler':
                if number > item[10]:
                    bot.send_message(
                        message.chat.id,
                        text=_('Неправильно выбранное количество. Пожалуйста, попробуйте еще раз', lang)
                    )
                elif db.count_cooler(item[0]) == 0:
                    bot.send_message(message.chat.id, text=_(
                        'Извините, но этот продукт не доступен', lang),
                        reply_markup=m.start_menu(message.chat.id, lang))
                    user_history[message.chat.id].append(message.text)
                else:
                    subtotal = number * item[9]

                    db.insert_cooler_order(
                        chat_id=message.chat.id,
                        date_created=date_created,
                        cooler_id=item[0],
                        id_def=item[1],
                        name=item[2],
                        cooler_definition=item[3],
                        price=item[9],
                        quantity=number,
                        subtotal=subtotal,
                        type=item[4],
                        capsule_setup=item[5],
                        heat=item[6],
                        width=item[7],
                        height=item[8]
                    )
                    db.minus_cooler_products(number=number, id=item[0])

                    bot.send_message(
                        chat_id=message.chat.id,
                        text=f'{_("Отличный выбор", lang)}'
                             f'\n{_("Хотите добавить еще что-то?", lang)}',
                        reply_markup=m.start_menu(message.chat.id, lang),
                    )
                    user_history[message.chat.id].append(message.text)

            elif item[1] == 'water':
                if number > item[7]:
                    bot.send_message(
                        message.chat.id,
                        text=_('Неправильно выбранное количество. Пожалуйста, попробуйте еще раз', lang)
                    )
                elif db.count_water(item[0]) == 0:
                    bot.send_message(message.chat.id, text=_(
                        'Извините, но этот продукт не доступен', lang),
                        reply_markup=m.start_menu(message.chat.id, lang))
                    user_history[message.chat.id].append(message.text)
                else:
                    subtotal = number * item[4]
                    db.insert_water_order(
                        chat_id=message.chat.id,
                        date_created=date_created,
                        water_id=item[0],
                        id_def=item[1],
                        product_id=item[6],
                        name=item[2],
                        water_definition=item[5],
                        price=item[4],
                        quantity=number,
                        subtotal=subtotal,
                        volume=item[3]
                    )
                    db.minus_water_products(number=number, id=item[0])

                    bot.send_message(
                        chat_id=message.chat.id,
                        text=f'{_("Отличный выбор", lang)}'
                             f'\n{_("Хотите добавить еще что-то?", lang)}',
                        reply_markup=m.start_menu(message.chat.id, lang),
                    )
                    user_history[message.chat.id].append(message.text)
        except Exception as e:
            bot.send_message(message.chat.id,
                 _("Что-то пошло не так. Пожалуйста, повторите попытку позже.",
                   lang))
            user_history[message.chat.id].append(message.text)


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

        water_order = db.get_water_order(message.text)
        if water_order and message.text == water_order[0][2]:
            item = db.get_water_order(message.text)[0]
            product = {
                'id': item[0],
                'type': item[1],
                _('Названия', lang): item[2],
                _('Объем', lang): item[3],
                _('Цена', lang): item[4],
                _('Описание', lang): item[5],
                'product_id': item[6],
                'quantity': item[7]
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

        cooler_order = db.get_cooler_order(message.text)
        if cooler_order and message.text == cooler_order[0][2]:
            item = db.get_cooler_order(message.text)[0]
            product = {
                'id': item[0],
                'type': item[1],
                _('Названия', lang): item[2],
                _('Описание', lang): item[3],
                _('Тип', lang): item[4],
                _('Установка капсул воды', lang): item[5],
                _('Нагрев', lang): item[6],
                _('Глубина', lang): item[7],
                _('Высота', lang): item[8],
                _('Цена', lang): item[9],
                'quantity': item[10]
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