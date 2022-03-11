import os
from PyQt5.QtWidgets import QMainWindow, QApplication
import sys
from bs4 import BeautifulSoup
import requests
import re
from urllib.request import urlopen
from playwright.sync_api import sync_playwright
from threading import Thread
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic

# carrega a UI
app = QApplication([])
window = uic.loadUi('layout_animes.ui')
window.frame.setVisible(False)
window.resize(500, 200)


class Funcao(Thread):
    # declarar as variaveis que terão interação da funcao com a interface UI
    def __init__(self, status, nome, inicio, fim, nome_completo):
        # variaveis que herdam os componentes
        self.status = status
        self.inicio = inicio
        self.fim = fim
        self.nome = nome
        self.nome_completo = nome_completo
        super().__init__()

    def funcaoExibir(self):
        # tenta criar a pasta para salvar o capitulo
        try:
            nome = str(self.nome_completo.currentItem().text()).split('/')[-1]
            os.mkdir(str(nome).upper())
            self.status.showMessage('Pasta criada com sucesso!')
        except Exception as e:
            pass

        print(f'{self.nome.text()} - {self.inicio.text()} - {self.fim.text()}')
        self.status.showMessage('')
        with open('episodios.txt', 'r') as f:
            linhas = f.readlines()
            for linha in linhas:
                linha = linha.replace('\n', '')
                # print(linha)
                link = linha.split(',')
                if link[0]:
                    if int(link[0]) >= int(self.inicio.text()) and int(link[0]) <= int(self.fim.text()):
                        ep = link[0]
                        with sync_playwright() as p:
                            self.status.showMessage(
                                'Capturando o link do video...')
                            browser = p.chromium.launch(headless=True)
                            page = browser.new_page()
                            # entra na pagina do anime
                            page.goto(link[1])
                            player = page.inner_html('#Player1')
                            soup = BeautifulSoup(player, 'html.parser')
                            links = soup.find('iframe')
                            link = links.attrs['src']

                            # entra na pagina do video
                            page.goto(link)
                            URL = page.content()
                            soup = BeautifulSoup(URL, 'html.parser')
                            links = soup.find('iframe')
                            link = links.attrs['src']

                            # baixa o video
                            page.goto(link)
                            URL = page.content()
                            soup = BeautifulSoup(URL, 'html.parser')
                            links = soup.find('video')
                            link_down = links.attrs['src']
                            print(link_down)

                            # download
                            r = requests.get(link_down, allow_redirects=True)
                            print(f'{self.nome.text()}_{link[0]}.mp4')
                            self.status.showMessage(
                                f'baixando {self.nome.text()}_{ep}.mp4')
                            open(f'{nome}/{self.nome.text()}_{ep}.mp4', 'wb').write(
                                r.content)
                            self.status.showMessage('Download concluido!')

    def run(self):
        self.funcaoExibir()


class Animes:
    def pesquisa_animes(self, nome):
        window.frame.setVisible(False)
        window.resize(500, 200)
        url = 'https://animesonline.club/busca?q=' + nome
        # pega o html da pagina
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        anime = []
        filme = []
        with open('animes.txt', 'w') as f:
            for link in soup.find_all('a', href=re.compile('/anime/')):
                anime.append(link.get('href'))

            # for link in soup.find_all('a', href=re.compile('/filme/')):
            #     filme.append(link.get('href'))
        window.lista_animes.clear()
        for i in anime:
            window.lista_animes.addItem(i)
        # for i in filme:
        #     window.lista_animes.addItem(i)

    def pesquisa_episodio(self, url):
        window.frame.setVisible(True)
        window.resize(500, 600)

        # variavel de controle para baixar os eps
        conteudo = []
        # pega o html da pagina
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')

        # pega os links de todos os epsodios
        epsodios = soup.find_all('a', href=re.compile('/episodio/'))
        # pega os capitulos de cada episodio
        nomes = soup.find_all('span', class_='nome')
        # pega o tipo dublado ou legendado + quantidade de episodios
        tipos = soup.find_all('div', class_='temporada-modo')
        window.lista_epsodios.clear()
        with open('episodios.txt', 'w') as f:
            cont = 1
            for tipo in tipos:
                versao = tipo.text.split('(')
                quantidade = int(versao[1][:-1])
                versao = versao[0]
                window.lista_epsodios.insertPlainText(
                    f'{versao} - {quantidade} episódios\n')

                for i in range(quantidade):
                    f.write(f'\n{cont}, {epsodios[i].get("href")}')
                    window.lista_epsodios.insertPlainText(
                        f'{cont} - {nomes[i].text}\n')
                    cont += 1
        return conteudo

    def baixa_mp4(self):
        t = Funcao(window.statusbar, window.ed_nome,
                   window.ed_inicio, window.ed_fim, window.lista_animes)
        retorno = t.start()


A = Animes()

# pesquisa o anime com o nome passado
window.bt_pesquisar.clicked.connect(
    lambda: A.pesquisa_animes(window.ed_nome.text()))

# com 2 cliques no anime, pega os episodios
window.lista_animes.doubleClicked.connect(
    lambda: A.pesquisa_episodio(window.lista_animes.currentItem().text()))


window.bt_baixar_eps.clicked.connect(lambda: A.baixa_mp4())

# exibe o programa
window.move(100, 100)
window.show()
app.exec()


# A.pesquisa_animes('naruto')
# A.pesquisa_episodio('https://animesonline.club/anime/boruto-naruto-next-generations')
# A.baixa_epsodio('https://animesonline.club/anime/boruto-naruto-next-generations/episodio/54943')
