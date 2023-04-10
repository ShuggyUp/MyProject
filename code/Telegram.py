import telebot
from telebot import types
import sqlite3 as sq


# @connect_to_bot.message_handler(commands=['start']) для обработки команд через /
# @connect_to_bot.message_handler() без параметров принимает любой текст


all_filters = ['junior', 'middle', 'senior']
with open('telegram_bot_token.txt', 'r') as file:
    connect_to_bot = telebot.TeleBot(file.readline())


def add_new_user_filter_to_db(chat_id, filters):
    with sq.connect('users_data.db') as connect_to_db:
        cursor = connect_to_db.cursor()
        filters_to_db_form = ' '.join(filters)
        cursor.execute(f"INSERT INTO users_data (chat_id, filters) VALUES ({chat_id}, '{filters_to_db_form}')")


def update_user_filter_to_db(chat_id, filter):
    with sq.connect('users_data.db') as connect_to_db:
        cursor = connect_to_db.cursor()
        user_db_filters = read_user_filter_from_db(chat_id)
        user_db_filters_list = user_db_filters.split()

        if filter not in user_db_filters_list:
            user_db_filters_list.append(filter)
            filters_to_db_form = ' '.join(user_db_filters_list)
            cursor.execute(f"UPDATE users_data SET filters = '{filters_to_db_form}' WHERE chat_id = {chat_id}")


def delete_user_filter_from_db(chat_id, filter):
    with sq.connect('users_data.db') as connect_to_db:
        cursor = connect_to_db.cursor()
        user_db_filters = read_user_filter_from_db(chat_id)
        user_db_filters_list = user_db_filters.split()
        user_db_filters_list.remove(filter)
        filters_to_db_form = ' '.join(user_db_filters_list)
        cursor.execute(f"UPDATE users_data SET filters = '{filters_to_db_form}' WHERE chat_id = {chat_id}")


def read_user_filter_from_db(chat_id):
    with sq.connect('users_data.db') as connect_to_db:
        cursor = connect_to_db.cursor()
        cursor.execute(f"SELECT filters FROM users_data WHERE chat_id = {chat_id}")
        user_db_filters = cursor.fetchone()[0]
    return user_db_filters


@connect_to_bot.message_handler(commands=['start'])
def output_start_message(chat_data):
    base_filters = ['junior']
    add_new_user_filter_to_db(chat_data.chat.id, base_filters)

    connect_to_bot.send_message(chat_data.chat.id, 'Здравствуйте!')


@connect_to_bot.message_handler(commands=['help'])
def output_all_command(chat_data):
    connect_to_bot.send_message(chat_data.chat.id, 'Доступные команды:\n/start\n/help\n'
                                                   '/setfilter\n/showfilter\n/delfilter')


@connect_to_bot.message_handler(commands=['setfilter'])
def set_filter(chat_data):
    button_creator = types.InlineKeyboardMarkup()
    user_db_filters = read_user_filter_from_db(chat_data.chat.id)
    user_db_filters_list = user_db_filters.split()

    available_filters = list(set(all_filters).difference(set(user_db_filters_list)))
    for filter in available_filters:
        button_creator.add(types.InlineKeyboardButton(filter.capitalize(), callback_data=f'set_filter_{filter}'))

    if len(available_filters) == 0:
        message_to_user = 'Все возможные фильтры были добавлены!'
    else:
        message_to_user = 'Доступные фильтры для добавления:'
        set_exit_bt = types.InlineKeyboardButton('Выход', callback_data='exit')
        button_creator.row(set_exit_bt)

    #set_junior_bt = types.InlineKeyboardButton('Junior', callback_data='filter_param_junior')
    #set_middle_bt = types.InlineKeyboardButton('Middle', callback_data='filter_param_middle')
    #set_senior_bt = types.InlineKeyboardButton('Senior', callback_data='filter_param_senior')
    #button_creator.row(set_junior_bt, set_middle_bt, set_senior_bt)

    connect_to_bot.send_message(chat_data.chat.id, message_to_user, reply_markup=button_creator)


@connect_to_bot.callback_query_handler(func=lambda callback: 'set_filter_' in callback.data)
def add_filter_param(callback_chat_data):
    filter_param = callback_chat_data.data.split('_')[2]
    update_user_filter_to_db(callback_chat_data.message.chat.id, filter_param)


@connect_to_bot.message_handler(commands=['delfilter'])
def delete_filter(chat_data):
    button_creator = types.InlineKeyboardMarkup()
    user_db_filters = read_user_filter_from_db(chat_data.chat.id)
    user_db_filters_list = user_db_filters.split()

    for item in user_db_filters_list:
        button_creator.add(types.InlineKeyboardButton(item.capitalize(), callback_data=f'del_filter_{item}'))

    if len(user_db_filters_list) == 0:
        message_to_user = 'Все возможные фильтры были удалены!'
    else:
        message_to_user = 'Доступные фильтры для удаления:'
        set_exit_bt = types.InlineKeyboardButton('Выход', callback_data='exit')
        button_creator.row(set_exit_bt)

    connect_to_bot.send_message(chat_data.chat.id, message_to_user, reply_markup=button_creator)


@connect_to_bot.callback_query_handler(func=lambda callback: 'del_filter_' in callback.data)
def delete_filter_param(callback_chat_data):
    filter_param = callback_chat_data.data.split('_')[2]
    delete_user_filter_from_db(callback_chat_data.message.chat.id, filter_param)


@connect_to_bot.callback_query_handler(func=lambda callback: callback.data == 'exit')
def exit_filter_menu(callback_chat_data):
    connect_to_bot.delete_message(callback_chat_data.message.chat.id, callback_chat_data.message.message_id)
    connect_to_bot.delete_message(callback_chat_data.message.chat.id, callback_chat_data.message.message_id - 1)
    connect_to_bot.send_message(callback_chat_data.message.chat.id, 'Фильтры изменены!')


@connect_to_bot.message_handler(commands=['showfilter'])
def show_filter(chat_data):
    user_db_filters = read_user_filter_from_db(chat_data.chat.id)
    user_db_filters = user_db_filters.replace(' ', ', ')
    connect_to_bot.send_message(chat_data.chat.id, f'Ваши фильтры: {user_db_filters}')


@connect_to_bot.message_handler()
def process_user_message(chat_data):
    connect_to_bot.send_message(chat_data.chat.id, 'Пожалуйста введите существующую команду!\n'
                                                   'Список можно посмотреть с помощью /help')


connect_to_bot.infinity_polling()
