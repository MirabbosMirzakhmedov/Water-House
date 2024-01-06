import sqlite3, schedule, time

class Database:
    def __init__(self, db_file):
        self.db_file = db_file

    def _create_connection(self):
        return sqlite3.connect(self.db_file)

    def user_exists(self, chat_id):
        with self._create_connection() as connection:
            cursor = connection.cursor()
            result = cursor.execute("SELECT * FROM users WHERE chat_id = ?", (chat_id,)).fetchall()
            return bool(len(result))

    def add_user(self, chat_id, lang):
        with self._create_connection() as connection:
            cursor = connection.cursor()
            return cursor.execute(
                "insert into users (chat_id, lang) values (?, ?)", (chat_id,
                                                                    lang,))

    def set_active(self, chat_id, active):
        with self._create_connection() as connection:
            cursor = connection.cursor()
            return cursor.execute("update `users` set `active` = ? "
                                       "where `chat_id` = ?", (active, chat_id))

    def get_users(self):
        with self._create_connection() as connection:
            cursor = connection.cursor()
            return cursor.execute('select `chat_id`, `active` from '
                                       'users').fetchall()

    def get_lang(self, chat_id):
        with self._create_connection() as connection:
            cursor = connection.cursor()
            return cursor.execute('select lang from users where chat_id = ?',
                                  (chat_id,)).fetchone()[0]

    def update_lang(self, lang, chat_id):
        with self._create_connection() as connection:
            cursor = connection.cursor()
            return cursor.execute("update `users` set `lang` = ? "
                                  "where `chat_id` = ?", (lang, chat_id))

    def get_products(self):
        with self._create_connection() as connection:
            cursor = connection.cursor()
            return cursor.execute('select `name_ru`, `name_uz` from '
                                  '`products_type`').fetchall()

    def get_water(self, product_id):
        pro = product_id
        with self._create_connection() as connection:
            cursor = connection.cursor()
            query = (
                'SELECT wb."name" FROM "water_bottle" wb '
                'JOIN `products_type` pt ON wb.product_id = pt.product_id '
                'WHERE wb.product_id = ?'
            )
            return cursor.execute(query, (product_id,)).fetchall()

    def get_product_id(self, name):
        with self._create_connection() as connection:
            cursor = connection.cursor()
            query = 'SELECT `product_id` FROM `products_type` ' \
                    'WHERE name_ru = ? OR name_uz = ?'
            result = cursor.execute(query, (name, name)).fetchone()
            return result[0] if result else None

    def get_coolers(self):
        with self._create_connection() as connection:
            cursor = connection.cursor()
            return cursor.execute('select `name` from '
                                  '`water_cooler`').fetchall()

    def get_water_by_product_id(self, product_id):
        with self._create_connection() as connection:
            cursor = connection.cursor()
            query = "SELECT * FROM water_bottle WHERE product_id = %s"
            cursor.execute(query, (product_id,))
            return cursor.fetchall()

    def get_water_order(self, name):
        with self._create_connection() as connection:
            cursor = connection.cursor()
            query = "SELECT * FROM water_bottle WHERE name = ?"
            cursor.execute(query, (name,))
            return cursor.fetchall()

    def get_cooler_order(self, name):
        with self._create_connection() as connection:
            cursor = connection.cursor()
            query = "SELECT * FROM water_cooler WHERE name = ?"
            cursor.execute(query, (name,))
            return cursor.fetchall()

    def get_water_image(self, water_id):
        try:
            with self._create_connection() as connection:
                connection.text_factory = bytes
                cursor = connection.cursor()
                query = "SELECT photo FROM images WHERE water_id = ?"
                cursor.execute(query, (water_id,))
                result = cursor.fetchone()
                if result:
                    return result[0]
                else:
                    return None
        except Exception as e:
            return None

    def get_cooler_image(self, cooler_id):
        try:
            with self._create_connection() as connection:
                connection.text_factory = bytes
                cursor = connection.cursor()
                query = "SELECT photo FROM images WHERE cooler_id = ?"
                cursor.execute(query, (cooler_id,))
                result = cursor.fetchone()
                if result:
                    return result[0]
                else:
                    return None
        except Exception as e:
            return None

    def update_water_order(self, chat_id, quantity, water_id):
        with self._create_connection() as connection:
            cursor = connection.cursor()
            query = "UPDATE orders SET " \
                    "water_quantity = ?," \
                    "chat_id = ?" \
                    "WHERE water_id = ?"
            cursor.execute(query, (quantity, chat_id, water_id,))
            return cursor.fetchall()

    def insert_cooler_order(
            self, chat_id, date_created, cooler_id, id_def, name, cooler_definition, price,
            quantity, subtotal, type, capsule_setup, heat, width,
            height):
        with self._create_connection() as connection:
            cursor = connection.cursor()
            query = ("INSERT INTO basket ("
                     "chat_id, date_created, cooler_id, "
                     "id_def, name, cooler_definition, "
                     "price, quantity, subtotal, type, capsule_setup, "
                     "heat, width, height) "
                     "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")

            cursor.execute(query, (
                chat_id, date_created, cooler_id,
                id_def, name, cooler_definition,
                price, quantity, subtotal, type,
                capsule_setup, heat, width, height,))
            connection.commit()

    def insert_water_order(
            self, chat_id, date_created, water_id, id_def,
            product_id, name, water_definition, price, volume,
            quantity, subtotal):
        with self._create_connection() as connection:
            cursor = connection.cursor()
            query = ("INSERT INTO basket ("
                     "chat_id, date_created, water_id, "
                     "id_def, product_id, name, water_definition, "
                     "price, volume, quantity, subtotal) "
                     "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")

            cursor.execute(query, (
                chat_id, date_created, water_id,
                id_def, product_id, name, water_definition,
                price, volume, quantity, subtotal,))
            connection.commit()

    def get_water_amount(self, id):
        with self._create_connection() as connection:
            cursor = connection.cursor()
            query = "SELECT quantity FROM water_bottle WHERE id = ?"
            cursor.execute(query, (id,))
            result = cursor.fetchone()

            if result is not None:
                return result[0]
            else:
                return None

    def get_cooler_amount(self, id):
        with self._create_connection() as connection:
            cursor = connection.cursor()
            query = "SELECT quantity FROM water_cooler WHERE id = ?"
            cursor.execute(query, (id,))
            result = cursor.fetchone()

            if result is not None:
                return result[0]
            else:
                return None

    def count_cooler(self, item_id):
        with self._create_connection() as connection:
            cursor = connection.cursor()
            query = "select quantity from water_cooler where id = ?"
            cursor.execute(query, (item_id,))
            result = cursor.fetchone()

            if result is not None:
                return result[0]
            else:
                return None

    def count_water(self, item_id):
        with self._create_connection() as connection:
            cursor = connection.cursor()
            query = "select quantity from water_bottle where id = ?"
            cursor.execute(query, (item_id,))
            result = cursor.fetchone()

            if result is not None:
                return result[0]
            else:
                return None

    def see_basket(self, chat_id):
        try:
            with self._create_connection() as connection:
                cursor = connection.cursor()
                query = (
                    "SELECT b.basket_id, b.chat_id, COALESCE(wb.name, wc.name) AS product_name, "
                    "COALESCE(wb.id, wc.id) AS product_id, COALESCE(wb.id_def, wc.id_def) AS product_id_def, "
                    "b.quantity, COALESCE(wb.price, wc.price) AS price, b.date_created, b.subtotal "
                    "FROM basket b "
                    "LEFT JOIN water_bottle wb ON b.water_id = wb.id "
                    "LEFT JOIN water_cooler wc ON b.cooler_id = wc.id "
                    "WHERE b.chat_id = ?"
                )
                cursor.execute(query, (chat_id,))
                result = cursor.fetchall()
                if result:
                    return result
                else:
                    return None
        except Exception as e:
            return None

    def minus_water_products(self, number, id):
        with self._create_connection() as connection:
            cursor = connection.cursor()
            query = ("UPDATE water_bottle SET quantity = quantity - ? "
                     "WHERE id = ?;")
            cursor.execute(query, (number, id,))
            result = cursor.fetchone()
            return result

    def minus_cooler_products(self, number, id):
        with self._create_connection() as connection:
            cursor = connection.cursor()
            query = ("UPDATE water_cooler SET quantity = quantity - ? "
                     "WHERE id = ?;")
            cursor.execute(query, (number, id,))
            result = cursor.fetchone()
            return result

    def empty_basket(self, chat_id):
        with self._create_connection() as connection:
            cursor = connection.cursor()
            query = ("DELETE FROM basket WHERE chat_id = ?;")
            cursor.execute(query, (chat_id,))
            result = cursor.fetchall()
            return result

    def update_water_stock(self, quantity, chat_id):
        with self._create_connection() as connection:
            cursor = connection.cursor()
            query = ("UPDATE water_bottle SET quantity = quantity + ? "
                     "WHERE id IN ("
                     "SELECT water_id FROM basket WHERE chat_id = ?);")
            cursor.execute(query, (quantity, chat_id,))
            result = cursor.rowcount
            return result

    def update_cooler_stock(self, quantity, chat_id):
        with self._create_connection() as connection:
            cursor = connection.cursor()
            query = ("UPDATE water_cooler SET quantity = quantity + ? "
                     "WHERE id IN ("
                     "SELECT cooler_id FROM basket WHERE chat_id = ?);")
            cursor.execute(query, (quantity, chat_id,))
            result = cursor.rowcount
            return result

    def get_water_id(self, chat_id):
        with self._create_connection() as connection:
            cursor = connection.cursor()
            select_query = "SELECT water_id, quantity FROM basket WHERE chat_id = ?;"
            cursor.execute(select_query, (chat_id,))
            records = cursor.fetchall()
            for record in records:
                water_id, quantity = record

                return water_id, quantity

    def get_cooler_id(self, chat_id):
        with self._create_connection() as connection:
            cursor = connection.cursor()
            select_query = "SELECT cooler_id, quantity FROM basket WHERE chat_id = ?;"
            cursor.execute(select_query, (chat_id,))
            records = cursor.fetchall()
            for record in records:
                water_id, quantity = record

                return water_id, quantity

    def get_delivery_buttons(self):
        buttons = []
        with self._create_connection() as connection:
            cursor = connection.cursor()
            query = "select * from delivery_buttons;"
            cursor.execute(query,)
            results = cursor.fetchall()
            for result in results:
                button_id, name_ru, name_uz = result
                buttons.append([button_id, name_ru, name_uz])
        return buttons

    def generate_excel(self):
        with self._create_connection() as connection:
            cursor = connection.cursor()
            query = "select * from water_bottle;" # can be changed to orders table
            cursor.execute(query,)
            results = cursor.fetchall()
            return results

    def get_admins(self):
        with self._create_connection() as connection:
            cursor = connection.cursor()
            query = "SELECT chat_id FROM users WHERE role = ?"
            cursor.execute(query, ('admin',))
            results = cursor.fetchall()
            return results