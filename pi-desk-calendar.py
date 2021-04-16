#!/usr/bin/env python3
"""Python Desktop Calendar."""

import json
import sys

from datetime import date, datetime
from time import sleep
from operator import itemgetter
from functools import cmp_to_key

import requests
import xmltodict

from inky import InkyWHAT
from PIL import Image, ImageFont, ImageDraw
from font_fredoka_one import FredokaOne

sys.getdefaultencoding()

def read_config():
    """Read Calendar Config File."""
    config_file = "./config.json"
    with open(config_file) as f:
        data = json.load(f)
    return data


def request_data(url):
    """Request data from Board Game Geek."""
    data = requests.get(url)
    return data.content


def get_hot_games():
    """Get top ten games on Board Game Geek hot games list."""
    url = "https://www.boardgamegeek.com/xmlapi2/hot?boardgames"
    game_data = xmltodict.parse(request_data(url))
    hot_games = ""
    count = 0
    for game in game_data['items']['item']:
        if count < 10:
            hot_games += "{0:<3}{1}\n".format(game['@rank'],
                          game['name']['@value'])
            count += 1
        else:
            break
    return hot_games


def weighted_average(rating, mean, plays):
    """Calculate weighted average for game."""
    rating, mean, plays = float(rating), float(mean), float(plays)
    minimum_plays = 25
    rating = (plays / (plays + minimum_plays)) * rating \
        + (minimum_plays / (plays + minimum_plays)) * mean
    return rating


def multi_key_sort(items, columns):
    """Sort dictionary based on multiple keys."""
    comparers = [((itemgetter(col[1:].strip()), 1) if col.startswith('-') else
                  (itemgetter(col.strip()), -1)) for col in columns]

    def comparer(left, right):
        for _fn, mult in comparers:
            result = ((_fn(left) > _fn(right)) - (_fn(left) < _fn(right)))
            if result:
                return mult * result
        return None

    return sorted(items, key=cmp_to_key(comparer))


def calculate_mean(collection):
    """Calculate the mean ration for collection."""
    ratings = []
    for game in collection['items']['item']:
        ratings.append(float(game['stats']['rating']['@value']))
    mean = sum(ratings)/len(ratings)
    return mean


def get_collection():
    """Get user's collection from BGG."""
    collection = []
    retry = 0
    config = read_config()
    username = config['bgg']['username']
    baseurl = 'https://www.boardgamegeek.com/xmlapi2/'
    url = baseurl + ('collection?username={}&own=1'
                     '&rated=1&played=1&stats=1').format(username)
    data = request_data(url)
    doc = xmltodict.parse(data)
    mean_rating = calculate_mean(doc)
    try:
        for game in doc['items']['item']:
            title = game['name']['#text'].encode('utf-8').strip()
            player_rating = game['stats']['rating']['@value']
            plays = game['numplays']
            rating = weighted_average(player_rating, mean_rating, plays)
            collection.append({'name': title, 'player_rate': player_rating,
                                'rating': rating, 'plays': plays})
    except KeyError:
        if retry < 5:
            retry += 1
            get_collection()
        else:
            collection = ("Could not fetch collection from BGG.")
            return collection

    collection = multi_key_sort(collection, ['rating', 'name'])

    return collection


def get_personal_top_ten():
    """Get personal top ten games using weighted average."""
    top_games = ""
    rank = 1
    collection = get_collection()
    for game in collection:
        top_games += "{0}{1}\n".format(str(rank).ljust(3), str(
            game['name']).strip('b').strip('\'').strip('\"'))
        if rank <= 9:
            rank += 1
        else:
            break
    return top_games

def calc_date_delta(different_date):
    """Calculate delta between two dates."""
    today = date.today()
    delta = different_date - today
    return delta.days

def convention_countdown():
    """Calculate the number of days until a given convention."""
    data = read_config()
    convention_list = ""
    for convention in data['game_conventions']:
        days_between = calc_date_delta(datetime.strptime(convention['start_date'], "%Y-%m-%d").date())
        if days_between < 0:
            continue
        elif days_between == 1:
            convention_list += "{0}: {1} day\n".format(convention['name'], delta.days)
        elif days_between == 0:
            convention_list += "{0}: Starts Today!\n".format(convention['name'], delta.days)
        else:
            convention_list += "{0}: {1} days\n".format(convention['name'], delta.days)
    return convention_list


def get_last_played_game():
    config = read_config()
    username = config['bgg']['username']
    baseurl = 'https://www.boardgamegeek.com/xmlapi2/'
    url = baseurl + "plays?username={}".format(username)
    data = request_data(url)
    doc = xmltodict.parse(data)
    count = 0
    last_played = ""
    for play in doc['plays']['play']:
        days_between = abs(calc_date_delta(datetime.strptime(play['@date'], "%Y-%m-%d").date()))
        last_played =+ "{}".format(play['item']['@name'])
        last_played =+ "{}: {} since last played.\n".format(play['@date'], days_between)
        if count < 2:
            count += 1
        else:
            break
    return last_played
            

def dispaly_calendar_page(title, page_content, font_size):
    """Display calendar page."""
    inky_display = InkyWHAT("red")
    inky_display.set_border(inky_display.BLACK)
    img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
    draw = ImageDraw.Draw(img)

    date_font = ImageFont.truetype(FredokaOne, 32)
    title_font = ImageFont.truetype(FredokaOne, 22)
    page_content_font = ImageFont.truetype(FredokaOne, font_size)

    padding = 20

    today = date.today().strftime("%B %d, %Y")

    # Display Date Banner
    for y in range(0,(5 + date_font.getsize(today)[1])):
        for x in range(0, inky_display.WIDTH):
            img.putpixel((x,y), inky_display.RED)
    w,h = date_font.getsize(today)
    x_today = (inky_display.WIDTH / 2 ) - (w / 2)
    y_today = 0
    draw.text((x_today, y_today), today, inky_display.WHITE, date_font)

    # Display Page Title
    w,h = title_font.getsize(title)
    x_title = (inky_display.WIDTH / 2) - (w / 2)
    y_title = y_today + padding + h
    draw.text((x_title, y_title), title, inky_display.BLACK, title_font)

    #Display Page Content
    w,h = page_content_font.getsize(page_content)
    x_content = 5
    y_content = y_title + padding + h
    draw.text((x_content, y_content), page_content, inky_display.BLACK, page_content_font)

    # For Testing
    flipped = img.rotate(180)

    inky_display.set_image(flipped)
    inky_display.show()

if __name__ == "__main__":
    dispaly_calendar_page("Top 10 Hot Games", get_hot_games(), 15)
    sleep(15)
    dispaly_calendar_page("Convention Countdown", convention_countdown(), 20)
    sleep(15)
    dispaly_calendar_page("Personal Top 10 Games", get_personal_top_ten(), 15)
    sleep(15)
    dispaly_calendar_page("Last 3 Games Played", get_last_played_game(), 20)