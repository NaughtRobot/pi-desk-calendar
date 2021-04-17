#!/usr/bin/env python3
"""Python Desktop Calendar."""

import json
import sys

from datetime import date, datetime
from time import sleep
from operator import itemgetter
from functools import cmp_to_key
from itertools import islice

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
    return xmltodict.parse(data.content)

def calc_date_delta(convention_start_date):
    """Calculate delta between two dates."""
    today = date.today()
    delta = convention_start_date - today
    return delta.days

def display_calendar_page(font_size, page_title, page_content):
    """Display calendar page."""
    today = date.today().strftime("%B %d, %Y")
    inky_display = InkyWHAT("red")
    inky_display.set_border(inky_display.BLACK)
    img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
    draw = ImageDraw.Draw(img)

    date_font = ImageFont.truetype(FredokaOne, 30)
    title_font = ImageFont.truetype(FredokaOne, 20)
    page_content_font = ImageFont.truetype(FredokaOne, font_size)
    
    padding = 15

    # Display Date Banner
    for y in range(0,(5 + date_font.getsize(today)[1])):
        for x in range(0, inky_display.WIDTH):
            img.putpixel((x,y), inky_display.RED)
    w,h = date_font.getsize(today)
    x_today = (inky_display.WIDTH / 2 ) - (w / 2)
    y_today = 0
    draw.text((x_today, y_today), today, inky_display.WHITE, date_font)
    
    # Display Page Title
    w,h = title_font.getsize(page_title)
    x_title = (inky_display.WIDTH / 2) - (w / 2)
    y_title = y_today + padding + h
    draw.text((x_title, y_title), page_title, inky_display.BLACK, title_font)

    #Display Page Content
    w,h = page_content_font.getsize(page_content)
    x_content = 5
    y_content = y_title + 5 + h
    draw.text((x_content, y_content), page_content, inky_display.BLACK, page_content_font)

    # For Testing
    flipped = img.rotate(180)

    inky_display.set_image(flipped)
    inky_display.show()

def display_hot_games():
    """Display top ten games on Board Game Geek hot games list."""
    hot_games_api = "https://www.boardgamegeek.com/xmlapi2/hot?boardgames"
    hot_games_data = request_data(hot_games_api)
    hot_games_list = ""
    count = 0
    for game in hot_games_data['items']['item']:
        if count < 10:
            hot_games_list += "{0:<3}{1}\n".format(game['@rank'],
                              game['name']['@value'])
            count += 1
        else:
            break

    display_calendar_page(15, "Top 10 Hot Games", hot_games_list)

def display_convention_countdown():
    """Calculate the number of days until a given convention."""   

    def calc_date_delta(convention_start_date):
        """Calculate delta between two dates."""
        today = date.today()
        delta = convention_start_date - today
        return delta.days  

    convention_data = read_config()
    convention_list = ""
    for convention in convention_data['game_conventions']:
        days_between = calc_date_delta(datetime.strptime(convention['start_date'], "%Y-%m-%d").date())
        if days_between < 0:
            continue
        elif days_between == 1:
            convention_list += "{} starts in {} day.\n".format(convention['name'], days_between)
        elif days_between == 0:
            convention_list += "{} starts today!\n".format(convention['name'], days_between)
        else:
            convention_list += "{} starts in {} days.\n".format(convention['name'], days_between)
    
    display_calendar_page(15, "Upcoming Gaming Conventions", convention_list)

def get_last_played_game():
    config = read_config()
    username = config['bgg']['username']
    baseurl = 'https://www.boardgamegeek.com/xmlapi2/'
    url = baseurl + "plays?username={}".format(username)
    last_played_data = request_data(url)
    count = 0
    last_games_played = ""
    for play in last_played_data['plays']['play']:
        last_games_played += "{}: {}\n".format(play['@date'], play['item']['@name'])
        if count < 10:
            count += 1
        else:
            break
    display_calendar_page(15, "Last 10 Games Played", last_games_played)


if __name__ == "__main__":
    display_hot_games()
    display_convention_countdown()
    get_last_played_game()