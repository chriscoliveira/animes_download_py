import urllib.request
from bs4 import BeautifulSoup
import requests
import re
import os
import sys
from os import supports_follow_symlinks
from time import sleep
from playwright.sync_api import sync_playwright


url = 'https://animesonline.club/anime/naruto-sd-rock-lee-no-seishun-full-power-ninden/episodio/41265'
page = requests.get(url)
soup = BeautifulSoup(page.text, 'html.parser')
link = ''
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    # entra na pagina do anime
    page.goto(url)
    player = page.inner_html('#Player1')
    soup = BeautifulSoup(player, 'html.parser')
    links = soup.find('iframe')
    link = links.attrs['src']
    print(f'link: nomral {link}')

    # entra na pagina do video
    page.goto(link)
    URL = page.content()
    soup = BeautifulSoup(URL, 'html.parser')
    links = soup.find('iframe')
    link = links.attrs['src']
    print(f'link: iframe {link}')

    # baixa o video
    page.goto(link)
    URL = page.content()
    soup = BeautifulSoup(URL, 'html.parser')
    links = soup.find('video')
    link_down = links.attrs['src']
    print(link_down)
