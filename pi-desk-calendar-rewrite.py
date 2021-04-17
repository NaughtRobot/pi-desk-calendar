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

def display_hot_games():
    """Display top ten games on Board Game Geek hot games list."""

    def display_calendar_page(page_content):
        """Display Hot Games calendar page."""
        today = date.today().strftime("%B %d, %Y")
        page_title = "Top 10 Hot Games"
        inky_display = InkyWHAT("red")
        inky_display.set_border(inky_display.BLACK)
        img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
        draw = ImageDraw.Draw(img)

        date_font = ImageFont.truetype(FredokaOne, 32)
        title_font = ImageFont.truetype(FredokaOne, 23)
        page_content_font = ImageFont.truetype(FredokaOne, 15)
        
        padding = 20

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
        y_content = y_title + padding + h
        draw.text((x_content, y_content), page_content, inky_display.BLACK, page_content_font)

        # For Testing
        flipped = img.rotate(180)

        inky_display.set_image(flipped)
        inky_display.show()

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

    display_calendar_page(hot_games_list)

if __name__ == "__main__":
    display_hot_games()