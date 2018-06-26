"""Planetakino parsers."""

import requests
from datetime import datetime

from bs4 import BeautifulSoup


def get_description(url):
    """Return description of film by parsing website=`url`."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    desc_div = soup.find('div', class_='movie-page-block__desc')
    description = desc_div.find('p').text.strip()

    return description


def get_sessions(soup, day, id):
    """Return list of available sessions at date=`day` for film with id=`id`."""
    sessions = []
    day_data = soup.find('day', attrs={'date': day.strftime('%Y-%m-%d')})
    for movie in day_data.find_all('show', attrs={'movie-id': id}):
        if movie.get('order-url'):
            session = '{time} ({technology})'.format(time=movie.get('time'),
                                                     technology=movie.get('technology'))
            sessions.append(session)

    return sorted(sessions)


def get_films_data(film):
    """Get data about films from `planatekino.ua`."""
    movies = {}
    response = requests.get(film.cinema)
    soup = BeautifulSoup(response.text, 'lxml')
    for movie in soup.find_all('movie'):
        start = movie.find('dt-start').text
        end = movie.find('dt-end').text
        if film.period >= datetime.strptime(start, '%Y-%m-%d') \
                and film.period <= datetime.strptime(end, '%Y-%m-%d'):
            title = movie.find('title').text
            url = movie.get('url')
            id = movie.get('id')
            sessions = get_sessions(soup, film.period, id)
            if sessions:
                description = get_description(url)
                movies[title] = {'url': url,
                                 'description': description,
                                 'sessions': sessions}

    return movies
