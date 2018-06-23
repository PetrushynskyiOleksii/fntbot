"""Simple telegram bot."""

from telebot import TeleBot, types
from config import token

bot = TeleBot(token)

film_dict = {}

cinema_dict = {'Forum': 'https://planetakino.ua/lvov2/showtimes/',
               'Kingcross': 'https://planetakino.ua/lvov/showtimes/'}
period_dict = {'Today': 'one-day',
               'Tomorrow': 'tomorrow',
               'Week': 'week',
               'Month': 'month'}


class TripToCinema:
    """Class that represent data about trip to the cinema."""

    def __init__(self):
        """Initialize data."""
        self.cinema = None
        self.period = None
        self.from_time = 0
        self.to_time = 0


@bot.message_handler(commands=['help', 'start'])
def handle_start_command(message):
    """Show keyboard."""
    markup_main = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup_main.row('Хочу сходити на фільмєц.')
    bot.send_message(message.from_user.id, 'Обери одну з кнопок нижче наведених.', reply_markup=markup_main)


@bot.message_handler(commands=['stop'])
def handle_stop_command(message):
    """Hide keyboard."""
    hide_markup = types.ReplyKeyboardRemove()
    bot.send_message(message.from_user.id, 'Покєда.', reply_markup=hide_markup)


@bot.message_handler(content_types=['text'])
def handle_buttons(message):
    """Perform the action according to the request."""
    if message.text == 'Хочу сходити на фільмєц.':
        markup_cinemas = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup_cinemas.row('Forum', 'Kingcross')
        msg = bot.send_message(message.from_user.id, 'Куди?', reply_markup=markup_cinemas)
        bot.register_next_step_handler(msg, process_cinemas_step)


def process_cinemas_step(message):
    """Create film object and update cinema field of film object with given data."""
    try:
        chat_id = message.chat.id
        film = TripToCinema()
        film_dict[chat_id] = film
        film.cinema = cinema_dict[message.text]

        markup_period = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup_period.row('Today', 'Tomorrow', 'Week', 'Month')
        msg = bot.send_message(message.from_user.id, 'Період?', reply_markup=markup_period)
        bot.register_next_step_handler(msg, process_time_step)

    except Exception as e:
        print(e)
        bot.reply_to(message, 'Упс..')


def process_time_step(message):
    """Update period field of film object with given data."""
    try:
        chat_id = message.chat.id
        film = film_dict[chat_id]
        film.period = period_dict[message.text]
        data = get_films_data(film) # noqa
    except Exception as e:
        print(e)
        bot.reply_to(message, 'oooops')


def get_films_data(film):
    """Get data about films from `planatekino`."""
    # TODO
    pass


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
