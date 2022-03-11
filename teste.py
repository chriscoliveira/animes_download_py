import urllib.request
from bs4 import BeautifulSoup
import requests
import re
import os
import sys
from os import supports_follow_symlinks
from time import sleep
from playwright.sync_api import sync_playwright

url = 'https://animesonline.club/play/serie/CG7A9TKJ5H01EFG'

with sync_playwright() as p:
    browser = p.firefox.launch(headless=True)
    page = browser.new_page()
    page.goto(url)
    page.screenshot(path="tela_anime.png")
    URL = page.content()
    soup = BeautifulSoup(URL, 'html.parser')
    links = soup.find('video')
    link = links.attrs['src']

    r = requests.get(link, allow_redirects=True)
    open('video.mp4', 'wb').write(r.content)
