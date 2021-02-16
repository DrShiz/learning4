import telebot
import os
import redis
from collections import defaultdict


token = os.getenv('TOKEN')
START, TITLE, LOCATION, CONFIRMATION = range(4)

USER_STATE = defaultdict(lambda: START)


def get_state(message):
    return USER_STATE[message.chat.id]


def update_state(message, state):
    USER_STATE[message.chat.id] = state


# PLACES = defaultdict(lambda: {})
#
#
# def get_place(user_id):
#     return PLACES[user_id]
#
#
# def update_place(user_id, key, value):
#     PLACES[user_id][key] = value


redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')

r = redis.from_url(redis_url, db=0, decode_responses=True)

bot = telebot.TeleBot(token)


def title_to_redis(message):
    user_id = message.chat.id
    title = message.text
    r.lpush(user_id, title)


def location_to_redis(user_id, location):
    lat, lon = location.latitude, location.longitude
    title = r.lpop(user_id)
    full_location_data = f'{title}&#124;{lat}&#124;{lon}'
    r.lpush(user_id, full_location_data)


def delete_location(user_id):
    r.lpop(user_id)


@bot.message_handler(func=lambda message: get_state(message) == START, commands=['add'])
def handle_message(message):
    bot.send_message(chat_id=message.chat.id, text='Напиши название места.')
    update_state(message, TITLE)


@bot.message_handler(func=lambda message: get_state(message) == TITLE)
def handle_title(message):
    if message.text in ('/add', '/list', '/reset'):
        update_state(message, START)
        delete_location(message.chat.id)
        bot.send_message(chat_id=message.chat.id, text='Добавление прервано')
    else:
        title_to_redis(message)
        bot.send_message(chat_id=message.chat.id, text='Пришли локацию.')
        update_state(message, LOCATION)


@bot.message_handler(func=lambda message: get_state(message) == LOCATION, content_types=['location'])
def handle_location(message):
    if message.text in ('/add', '/list', '/reset'):
        update_state(message, START)
        delete_location(message.chat.id)
        bot.send_message(chat_id=message.chat.id, text='Добавление прервано')
    else:
        location_to_redis(message.chat.id, message.location)
        bot.send_message(chat_id=message.chat.id, text='Запомнить место?')
        update_state(message, CONFIRMATION)


@bot.message_handler(func=lambda message: get_state(message) == CONFIRMATION)
def handle_confirmation(message):
    if message.text in ('/add', '/list', '/reset'):
        update_state(message, START)
        delete_location(message.chat.id)
        bot.send_message(chat_id=message.chat.id, text='Добавление прервано')
    else:
        if 'да' in message.text.lower():
            bot.send_message(chat_id=message.chat.id, text='Записал.')
            update_state(message, START)
        if 'нет' in message.text.lower():
            bot.send_message(chat_id=message.chat.id, text=f'Локация не добавлена')
            update_state(message, START)
            delete_location(message.chat.id)


@bot.message_handler(func=lambda x: True, commands=['list'])
def handle_list(message):
    if get_state(message) != START:
        update_state(message, START)
        r.lpop(message.chat.id)
    else:
        bot.send_message(chat_id=message.chat.id, text='Последние локации:')
        last_locations = r.lrange(message.chat.id, 0, 10)
        for location in last_locations:
            if '&#124;' in location:
                title, lat, lon = location.split('&#124;')
                bot.send_message(chat_id=message.chat.id, text=title)
                bot.send_location(message.chat.id, lat, lon)


@bot.message_handler(func=lambda x: True, commands=['reset'])
def handle_confirmation(message):
    r.flushdb()
    bot.send_message(chat_id=message.chat.id, text='Все локации удалены')


@bot.message_handler(func=lambda x: True, commands=['start'])
def handle_confirmation(message):
    bot.send_message(chat_id=message.chat.id, text='Введите команду /add для добавления локации')
    bot.send_message(chat_id=message.chat.id,
                     text='Введите команду /list для просмотра 10 последних локаций')
    bot.send_message(chat_id=message.chat.id,
                     text='Введите команду /reset для удаления всех локаций')


bot.polling()
