"""Planetakino parsers."""

import requests
from datetime import datetime
from bs4 import BeautifulSoup


def get_description(response):
    """Return description of film."""
    soup = BeautifulSoup(response.text, 'lxml')
    desc_div = soup.find('div', class_='movie-page-block__desc')
    description = desc_div.find('p').text.strip()

    return description


def get_sessions(response, date):
    """Return information about sessions at `date`."""
    sessions = []
    soup = BeautifulSoup(response.text, 'lxml')
    days_div = soup.find_all('div', class_='showtimes-row')

    for div in days_div:
        day_str = div.find('span', class_='date').text
        day_int = int(day_str.split()[0])

        if int(date.day) == day_int:
            for session in div.find_all('a', class_='time'):
                sessions.append(session.text.strip())

    return sessions


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
            response = requests.get(url)

            sessions = get_sessions(response, film.period)
            if sessions:
                description = get_description(response)
                movies[title] = {'url': url,
                                 'description': description,
                                 'sessions': sessions}

    return movies
