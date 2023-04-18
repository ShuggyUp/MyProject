import sqlite3 as sq


def check_user_data_existence(chat_id):
    with sq.connect('users_data.db') as connect_to_db:
        cursor = connect_to_db.cursor()
        existence = cursor.execute(f"SELECT EXISTS(SELECT * FROM users_data WHERE chat_id = {chat_id})").fetchone()
        if existence:
            return True
        else:
            return False


def add_new_user_filter_to_db(chat_id, filters):
    with sq.connect('users_data.db') as connect_to_db:
        cursor = connect_to_db.cursor()
        filters_to_db_form = ', '.join(filters)
        cursor.execute(f"INSERT INTO users_data (chat_id, filters) VALUES ({chat_id}, '{filters_to_db_form}')")


def update_user_filter_to_db(chat_id, filter_to_update):
    with sq.connect('users_data.db') as connect_to_db:
        cursor = connect_to_db.cursor()
        user_db_filters = read_user_filter_from_db(chat_id)

        if filter_to_update not in user_db_filters:
            user_db_filters.append(filter_to_update)
            filters_to_db_form = ', '.join(user_db_filters)
            cursor.execute(f"UPDATE users_data SET filters = '{filters_to_db_form}' WHERE chat_id = {chat_id}")


def delete_user_filter_from_db(chat_id, filter_to_del):
    with sq.connect('users_data.db') as connect_to_db:
        cursor = connect_to_db.cursor()
        user_db_filters = read_user_filter_from_db(chat_id)
        user_db_filters.remove(filter_to_del)
        filters_to_db_form = ', '.join(user_db_filters)
        cursor.execute(f"UPDATE users_data SET filters = '{filters_to_db_form}' WHERE chat_id = {chat_id}")


def read_user_filter_from_db(chat_id):
    with sq.connect('users_data.db') as connect_to_db:
        cursor = connect_to_db.cursor()
        cursor.execute(f"SELECT filters FROM users_data WHERE chat_id = {chat_id}")
        user_db_filters_list = cursor.fetchone()[0].split(', ')
    return user_db_filters_list


def read_users_data_from_db():
    with sq.connect('users_data.db') as connect_to_db:
        cursor = connect_to_db.cursor()
        cursor.execute(f"SELECT * FROM users_data")
        users_data = cursor.fetchall()
    return users_data
