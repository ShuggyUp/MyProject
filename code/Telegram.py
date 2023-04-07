import telebot
from telebot import types
import webbrowser
import json
import os

# @connect_to_bot.message_handler(commands=['start']) для обработки команд через /
# @connect_to_bot.message_handler() без параметров принимает любой текст


connect_to_bot = telebot.TeleBot('6126143333:AAGOhrq3iXwk4I8y7WOAj6OJdJ0kpiIdAzg')


def add_and_save_filter_param(chat_id, param):
    with open('users_data.txt', 'r') as file:
        if os.stat('users_data.txt').st_size != 0:
            for_all_users_filter_file = json.load(file)
        else:
            for_all_users_filter_file = {}

    if chat_id not in for_all_users_filter_file:
        for_all_users_filter_file[chat_id] = [param]
    else:
        if param not in for_all_users_filter_file[chat_id]:
            for_all_users_filter_file[chat_id] += [param]

    with open('users_data.txt', 'w') as file:
        json.dump(for_all_users_filter_file, file)


@connect_to_bot.message_handler(commands=['start'])
def output_start_message(chat_data):
    connect_to_bot.send_message(chat_data.chat.id, 'Дороу!')


@connect_to_bot.message_handler(commands=['help'])
def output_all_command(chat_data):
    connect_to_bot.send_message(chat_data.chat.id, 'Доступные команды:\n/start\n/help\n/roll\n/setfilter')


@connect_to_bot.message_handler(commands=['roll'])
def output_rickroll(chat_data):
    connect_to_bot.send_message(chat_data.chat.id, 'Вас зарикроллили!')
    webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")


@connect_to_bot.message_handler(commands=['setfilter'])
def set_filter(chat_data):
    button_creator = types.InlineKeyboardMarkup()
    set_junior_bt = types.InlineKeyboardButton('Junior', callback_data='filter_param_junior')
    set_middle_bt = types.InlineKeyboardButton('Middle', callback_data='filter_param_middle')
    set_senior_bt = types.InlineKeyboardButton('Senior', callback_data='filter_param_senior')
    button_creator.row(set_junior_bt, set_middle_bt, set_senior_bt)

    set_exit_bt = types.InlineKeyboardButton('Выход', callback_data='exit')
    button_creator.row(set_exit_bt)

    connect_to_bot.send_message(chat_data.chat.id, 'Доступные фильтры:', reply_markup=button_creator)


@connect_to_bot.callback_query_handler(func=lambda callback: 'filter_param_' in callback.data)
def add_filter_param(callback_chat_data):
    filter_param = callback_chat_data.data.split('_')[2]
    add_and_save_filter_param(str(callback_chat_data.message.chat.id), filter_param)


@connect_to_bot.callback_query_handler(func=lambda callback: callback.data == 'exit')
def exit_menu_filter(callback_chat_data):
    connect_to_bot.delete_message(callback_chat_data.message.chat.id, callback_chat_data.message.message_id)
    connect_to_bot.delete_message(callback_chat_data.message.chat.id, callback_chat_data.message.message_id - 1)
    connect_to_bot.send_message(callback_chat_data.message.chat.id, 'Фильтры установлены!')


@connect_to_bot.message_handler()
def process_user_message(chat_data):
    if chat_data.text.lower() == 'ы':
        connect_to_bot.send_message(chat_data.chat.id, 'А ну вернулся обратно на ветку, бубун!')


connect_to_bot.infinity_polling()
