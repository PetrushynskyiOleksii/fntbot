"""Telegram bot."""

import locale
import re
from time import sleep
from datetime import datetime, timedelta

from telebot import TeleBot, types

from config import token, cinema_dict
from parser import get_films_data
from logger import log_request_messages, log_uncorrect_messages

bot = TeleBot(token)
film_dict = {}


class FilmSession:
    """Class that represent film session data."""

    def __init__(self):
        """Initialize data."""
        self.today = today
        self.cinema = None
        self.period = None


@bot.message_handler(commands=['help'])
def handle_help_command(message):
    """Send help information in using the bot."""
    date = today.strftime('%d.%m')
    help_text = 'Для того, щоб дізнатись про усі доступні фільмєци ' \
                'черкани в діалозі команду /start. ' \
                'Бот задасть тобі лише два питання:\n' \
                '   \U00002753 У якому кінотеатрі?\n' \
                '   \U00002753 У який день?\n' \
                'До хвилини часу ти отримаєш інфу про назву фільму, ' \
                'години сеансів та силку, де ти зможеш придбати квиток.\n' \
                'Або одразу напиши текстове повідомлення у наступному вигляді: \n' \
                '   \U00002B55 kingcross, {}'.format(date)
    bot.send_message(message.from_user.id, help_text)


@bot.message_handler(commands=['start'])
def handle_start_command(message):
    """Show keyboard for cinema choice."""
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
    bot.send_message(message.from_user.id, 'Покєда, буду скучати (нет).', reply_markup=hide_markup)
    film_dict.pop(message.chat.id, None)


@bot.message_handler(regexp=r'(?i)(кк|kingcross|кінгкрос|форум|forum).+[0-9]{2}.[0-9]{2}')
def handle_film_request(message):
    """Handle a request that is presented as a text message."""
    result = parse_message(message.text)
    if result.get('is_parsed'):
        film = FilmSession()
        film.period = result.get('date')
        film.cinema = cinema_dict[result.get('cinema')]

        bot.send_chat_action(message.chat.id, 'typing')
        session_data = get_films_data(film)
        send_session_data(message.chat.id, session_data)
        bot.send_message(message.from_user.id,
                         '\U0001F3A5 Гарного перегляду!')
        log_request_messages(message.from_user, film)
    else:
        bot.send_message(message.from_user.id, result.get('error_message'))
        log_uncorrect_messages(message.from_user, message.text)


@bot.message_handler(content_types=['text'])
def handle_atypical_text_messages(message):
    """Handle atypical input messages."""
    bot.send_message(message.from_user.id,
                     'Я не твій кєнт і не розбираюсь у твоєму сленгу. '
                     'Пиши на моїй мові! Для детальної інформації черкани /help .')
    log_uncorrect_messages(message.from_user, message.text)


def process_cinema_step(message):
    """Create film object, update cinema field of created object."""
    film = FilmSession()
    days = []
    for i in range(1, 4):
        day = film.today + timedelta(days=1 + i)
        days.append(day.strftime('%d.%m, %a'))

    chat_id = message.chat.id
    film_dict[chat_id] = film
    film.cinema = cinema_dict[message.text]

    try:
        markup_days = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup_days.row('Сьогодні', 'Завтра')
        markup_days.row(days[0], days[1], days[2])
    except Exception as e:
        log_uncorrect_messages(message.from_user, 'EXC: cinema step')
        hide_markup = types.ReplyKeyboardRemove()
        bot.reply_to(message, 'Упс..Щось пішло не так. Cпробуй ще раз (/start).', reply_markup=hide_markup)

    msg = bot.send_message(message.from_user.id,
                           'А тепер день:  \U00002935',
                           reply_markup=markup_days)
    bot.register_next_step_handler(msg, process_days_step)


def process_days_step(message):
    """Update period field of film object with given data."""
    chat_id = message.chat.id
    film = film_dict[chat_id]
    try:
        if message.text == 'Сьогодні':
            film.period = film.today
        elif message.text == 'Завтра':
            film.period = film.today + timedelta(days=1)
        else:
            day, month, *other = re.split('[.,]', message.text)
            film.period = datetime(film.today.year, int(month), int(day))

        bot.send_chat_action(chat_id, 'typing')
        session_data = get_films_data(film)
        send_session_data(chat_id, session_data)

    except Exception as e:
        log_uncorrect_messages(message.from_user, 'EXC: days step')
        hide_markup = types.ReplyKeyboardRemove()
        bot.reply_to(message, 'Упс..Щось пішло не так. Cпробуй ще раз (/start).', reply_markup=hide_markup)

    log_request_messages(message.from_user, film)
    hide_markup = types.ReplyKeyboardRemove()
    bot.send_message(message.from_user.id,
                     '\U0001F3A5 Гарного перегляду!',
                     reply_markup=hide_markup)


def parse_message(message):
    """Parse message, return dict with information about date and cinema or error message."""
    result = {'is_parsed': False, 'error_message': None, 'date': None, 'cinema': None}
    forum = re.findall(r'(?i)(форум|forum)', message)
    kingcross = re.findall(r'(?i)(kingcross|кінгкрос|кк)', message)

    if forum:
        result['cinema'] = 'Forum'
    elif kingcross:
        result['cinema'] = 'Kingcross'
    else:
        result['error_message'] = 'Я в такі кінотеатри не ходжу. ' \
                                  'Обери або Kingcross, або Forum'
        return result

    parsed_date = re.findall(r'[0-3]{1}[0-9]{1}.[0-1]{1}[0-9]{1}', message)
    if parsed_date:
        day_str, month_str = parsed_date[0].split('.')
        day = int(day_str)
        month = int(month_str)
        if day not in range(1, 32) or month not in range(1, 13):
            result['error_message'] = 'То в твоєму селі така дата?'
            return result

        first_day = today
        last_day = first_day + timedelta(days=4)
        try:
            result['date'] = datetime(first_day.year, month, day)
        except ValueError:
            result['error_message'] = 'То в твоєму селі така дата?'
            return result

        if not first_day - timedelta(days=1) <= result.get('date') <= last_day:
            result['error_message'] = 'Можу дату інформацію лише ' \
                                      'в межах {} - {}'.format(first_day.strftime('%d.%m'),
                                                               last_day.strftime('%d.%m'))
            return result

    result['is_parsed'] = True
    return result


def send_session_data(chat_id, data):
    """Send information about sessions to chat=`chat_id`."""
    for key, value in data.items():
        title = key
        url = '{}{}'.format(value.get('url'), '#imax_cinetech_2d_3d_4dx_week')
        sessions = ', '.join(value.get('sessions'))
        description = value.get('description')

        formed_msg = '\U0001F538{}.\n{}\n' \
                     '\U0001F538Доступні сесії:' \
                     ' {}.\n{}'.format(title, description, sessions, url)

        bot.send_message(chat_id, formed_msg)
        sleep(2)


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    today = datetime.today()
    bot.polling(none_stop=True, interval=0)
