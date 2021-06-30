#!/usr/bin/python


# This file is part of clyrics.
#
#     clyrics is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     clyrics is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with clyrics.  If not, see <https://www.gnu.org/licenses/>.


import sys
import re

try:
    import mutagen
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print('failed to import modules')
    sys.exit(1)


# constants
URL = 'https://search.azlyrics.com/'
SEARCH = '/search.php'
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/78.0'


def get_song_data(f):
    """
    Returns the artist and title of the file in a single string
    """
    try:
        audio = mutagen.File(f, easy=True)
    except mutagen.MutagenError:
        print('failed to load file: ' + f)
        sys.exit(1)

    return audio['artist'][0] + ' ' + audio['title'][0]


def to_query_fmt(query):
    """
    Replaces all blank characters with +
    """
    return re.sub(' ', '+', query)


def search_song(song):
    """
    Queries a song and returns the url of the first result
    """
    data = requests.get(
        URL + SEARCH,
        params={'q': to_query_fmt(song)}, headers={
            'User-Agent': USER_AGENT
        }).text

    soup = BeautifulSoup(data, 'html.parser')

    # improve readability
    table = soup.find('table')
    first_result = table.find('tr')
    url = first_result.find('a').get('href')

    return url


def get_lyrics(url):
    """
    Prints the song lyrics
    """
    data = requests.get(url, headers={'User-Agent': USER_AGENT})
    # use proper charset
    data.encoding = data.apparent_encoding

    soup = BeautifulSoup(data.text, 'html.parser')

    for div in soup.find_all('div'):
        # the div containing the lyrics doesn't have an id nor a class
        if not div.get('class') and not div.get('id'):
            print(div.text)



def main():
    if len(sys.argv) < 2:
        print('Usage: clyrics.py [FILES]')
        sys.exit(1)

    for file in sys.argv[1:]:
        song = get_song_data(file)

        url = search_song(song)

        # the first element is the artist and the second element is the title
        print('Lyrics for ' + song)

        get_lyrics(url)


if __name__ == '__main__':
    main()
