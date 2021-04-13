#!/usr/bin/env python3
"""Python Desktop Calendar."""

import json

from datetime import date, datetime
from time import sleep

import requests
import xmltodict

from inky import InkyWHAT
from PIL import Image, ImageFont, ImageDraw
from font_fredoka_one import FredokaOne

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

def convention_countdown():
    """Calculate the number of days until a given convention."""
    data = read_config()
    today = date.today()
    convention_list = ""
    for convention in data['game_conventions']:
        start_date = datetime.strptime(convention['start_date'], "%Y-%M-%d").date()
        delta = today - start_date
        if delta.days == 1:
            convention_list = "{} day until {}.\n".format(delta.days, convention['name'])
        elif delta.days == 0:
            convention_list = "{} starts today\n".format(convention['name'])
        else:
            convention_list = "{} days until {}.\n".format(delta.days, convention['name'])
    return convention_list


def dispaly_calendar_page(title, page_content):
    """Display calendar page."""
    inky_display = InkyWHAT("red")
    inky_display.set_border(inky_display.BLACK)
    img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
    draw = ImageDraw.Draw(img)

    date_font = ImageFont.truetype(FredokaOne, 32)
    title_font = ImageFont.truetype(FredokaOne, 22)
    page_content_font = ImageFont.truetype(FredokaOne, 15)

    padding = 20

    today = date.today().strftime("%B %d, %Y")
    today

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
    dispaly_calendar_page("Top 10 Hot Games", get_hot_games())
    sleep(30)
    dispaly_calendar_page("Boad Game Convention Countdown", convention_countdown())