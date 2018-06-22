"""Simple telegram bot."""

from telebot import TeleBot, types
from .config import token

bot = TeleBot(token)


@bot.message_handler(commands=['start'])
def handle_start_command(message):
    """Show keyboard."""
    markup = types.ReplyKeyboardMarkup(True, False)
    markup.row('Where can i drunk?')
    bot.send_message(message.from_user.id, 'Choose button below.', reply_markup=markup)


@bot.message_handler(commands=['stop'])
def handle_stop_command(message):
    """Hide keyboard."""
    hide_markup = types.ReplyKeyboardRemove()
    bot.send_message(message.from_user.id, 'Thanks for using.', reply_markup=hide_markup)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
