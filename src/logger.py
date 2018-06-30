"""Loggers for telebot."""

import logging
import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('logs_info.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s -> %(message)s', '%d.%m %H:%M')
handler.setFormatter(formatter)
logger.addHandler(handler)


def log_request_messages(user, message):
    """Log OK request information."""
    user_information = 'OK  | {0: <8} {1: >8} {2: <15} | '.format(user.id,
                                                                  user.first_name,
                                                                  user.last_name)
    cinema = re.findall(r'lvov\d?', message.cinema)[0]
    if cinema == 'lvov':
        cinema = 'Kingcross'
    else:
        cinema = 'Forum'
    request_information = '{} {:%d.%m}'.format(cinema, message.period)

    logger.info(user_information + request_information)


def log_uncorrect_messages(user, message):
    """Log uncorrect input messages and bad requests."""
    user_information = 'Bad | {0: <8} {1: >8} {2: <15} | '.format(user.id,
                                                                  user.first_name,
                                                                  user.last_name)
    logger.info(user_information + message)
