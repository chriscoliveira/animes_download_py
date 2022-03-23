
import os
import re
from threading import Thread

import requests
from PyQt5 import uic
from PyQt5.QtWidgets import *
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def pesquisa_episodio(url):

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel='chrome', headless=True)
        page = browser.new_page()
        # entra na pagina do anime
        page.goto(url)
        player = page.inner_html('#episodios')
        soup = BeautifulSoup(player, 'html.parser')
        conteudo = soup.text
        with open('html.txt', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        with open('conteudo.txt', 'w', encoding='utf-8') as f:
            f.write(conteudo.replace('   ', '\n').replace(
                'LegendadoEpisódios', 'Legendado\nEpisódios').replace('DubladoEpisódios', 'Dublado\nEpisódios')
                .replace(' Ep.', 'Ep.')
                .replace(' Ep.', 'Ep.').replace('  Episódios ', '\nEpisódios ')
                .replace('  TEMPORADA', 'TEMPORADA').replace('Novo EpisódioEpisódios', 'Novo Episódio\nEpisódios')
                .replace('    Novo Episódio', ''))

        # pega os links de todos os epsodios
        epsodios = soup.find_all('a', href=re.compile('/episodio/'))
        # pega os capitulos de cada episodio
        nomes = soup.find_all('span', class_='nome')
        # pega o tipo dublado ou legendado + quantidade de episodios
        tipos = soup.find_all('div', class_='temporada-modo')
        #
        # window.lista_epsodios.clear()
        #
        # abre o conteudo.txt
        with open('conteudo.txt', 'r', encoding='utf-8') as contxt:
            with open('conteudo_final.txt', 'w', encoding='utf-8') as f:
                conteudo = contxt.readlines()
                for i in conteudo:
                    if 'Ep.' in i:
                        f.write(i)

            with open('episodios.txt', 'w') as f:

                for tipo in tipos:
                    versao = tipo.text.split('(')
                    print('versao: ', versao)
                    quantidade = int(versao[1][:-1])
                    print('quantidade: ', quantidade)
                    versao = versao[0]
                    print('versao[0]: ', versao)
                    # window.lista_epsodios.insertPlainText(
                    #     f'{versao} - {quantidade} episódios\n')
                    dub = versao.split(' ')

                    for i in range(quantidade):
                        nome = str(nomes[cont].text).replace('ó', 'o')
                        f.write(
                            f'\n{cont}, {epsodios[cont].get("href")}, {dub[1]} {nome}')
                        # window.lista_epsodios.insertPlainText(
                        #     f'{cont} - {nomes[i].text}\n')
                        print(f'{cont} - {nomes[i].text}\n')
                        cont += 1


# pesquisa_episodio('https://animesonline.club/anime/boku-no-hero-academia')
# pesquisa_episodio(
    # "https://animesonline.club/anime/naruto-shippuden-legendado-online")
pesquisa_episodio(
    'https://animesonline.club/anime/shingeki-no-kyojin-attack-on-titan-online')
