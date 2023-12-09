import sqlite3

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
            print(f"Error retrieving image: {e}")
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
            print(f"Error retrieving image: {e}")
            return None