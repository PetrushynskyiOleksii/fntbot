"""Telegram bot."""

import locale
from datetime import datetime, timedelta

from telebot import TeleBot, types

from config import token, cinema_dict
from parser import get_films_data

bot = TeleBot(token)
film_dict = {}
locale.setlocale(locale.LC_ALL, '')


class FilmSession:
    """Class that represent film session data."""

    def __init__(self):
        """Initialize data."""
        self.today = datetime.today()
        self.cinema = None
        self.period = None


@bot.message_handler(commands=['help', 'start'])
def handle_start_command(message):
    """Show keyboard for cinema choise."""
    markup_cinemas = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup_cinemas.row('Forum', 'Kingcross')
    msg = bot.send_message(message.from_user.id,
                           'Хочеш подивитись фільмєц? Обери кінотеатр:  \U00002935',
                           reply_markup=markup_cinemas)
    bot.register_next_step_handler(msg, process_cinema_step)


@bot.message_handler(commands=['stop'])
def handle_stop_command(message):
    """Hide keyboard."""
    hide_markup = types.ReplyKeyboardRemove()
    bot.send_message(message.from_user.id, 'Покєда.', reply_markup=hide_markup)
    film_dict.pop(message.chat.id, None)


def process_cinema_step(message):
    """Create film object, update cinema field of created object."""
    film = FilmSession()
    days = []
    for i in range(1, 4):
        day = film.today + timedelta(days=1 + i)
        days.append(day.strftime('%d.%m, %a'))

    try:
        chat_id = message.chat.id
        film_dict[chat_id] = film
        film.cinema = cinema_dict[message.text]

        markup_days = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup_days.row('Сьогодні', 'Завтра')
        markup_days.row(days[0], days[1], days[2])
        msg = bot.send_message(message.from_user.id,
                               'А тепер день:  \U00002935',
                               reply_markup=markup_days)
        bot.register_next_step_handler(msg, process_days_step)

    except Exception as e:
        print(e)
        bot.reply_to(message, 'Упс..Щось пішло не так. Cпробуй ще раз (/start)')


def process_days_step(message):
    """Update period field of film object with given data."""
    try:
        chat_id = message.chat.id
        film = film_dict[chat_id]

        if message.text == 'Сьогодні':
            film.period = film.today
        elif message.text == 'Завтра':
            film.period = film.today + timedelta(days=1)
        else:
            import re
            date_information = re.split('[.,]', message.text)
            film.period = datetime(film.today.year,
                                   int(date_information[1]),
                                   int(date_information[0]))

        bot.send_chat_action(chat_id, 'typing')
        data = get_films_data(film)
        for key, value in data.items():
            title = key
            url = value.get('url')
            sessions = ', '.join(value.get('sessions'))
            description = value.get('description')

            formed_msg = '\U0001F538{}.\n{}\n' \
                         '\U0001F538Доступні сесії:' \
                         ' {}.\n{}'.format(title, description, sessions, url)

            bot.send_message(message.from_user.id, formed_msg)

    except Exception as e:
        print(e)
        bot.reply_to(message, 'Упс..Щось пішло не так. Cпробуй ще раз (/start).')


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
