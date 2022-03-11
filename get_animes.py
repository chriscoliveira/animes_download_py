
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


class Funcao(Thread):
    # declarar as variaveis que terão interação da funcao com a interface UI
    def __init__(self, status, nome, inicio, fim):
        # variaveis que herdam os componentes
        self.status = status
        self.inicio = inicio
        self.fim = fim
        self.nome = nome

        super().__init__()

    def funcaoExibir(self):
        print(f'{self.nome.text()} - {self.inicio.text()} - {self.fim.text()}')
        with open('episodios.txt', 'r') as f:
            linhas = f.readlines()
            for linha in linhas:
                linha = linha.replace('\n', '')
                # print(linha)
                link = linha.split(',')

                try:
                    if int(link[0]) >= int(self.inicio.text()) and int(link[0]) <= int(self.fim.text()):
                        print(link[1])
                        self.status.showMessage(
                            f'Baixando o episódio {link[0]} de {self.nome.text()}')
                        with sync_playwright() as p:
                            browser = p.firefox.launch(headless=True)
                            page = browser.new_page()
                            page.goto(link[1])
                            print(link)
                            # page.screenshot(path="tela_anime.png")
                            URL = page.content()
                            soup = BeautifulSoup(URL, 'html.parser')
                            links = soup.find('video')
                            link = links.attrs['src']
                            self.status.showMessage(
                                f'Baixando o episódio {link[0]} de {self.nome.text()}')
                            r = requests.get(link, allow_redirects=True)
                            open(f'{self.nome}_ep{link[0]}.mp4', 'wb').write(
                                r.content)
                except Exception as e:
                    print('erro' + str(e))

    def run(self):
        self.funcaoExibir()


class Animes:
    def pesquisa_animes(self, nome):
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

    def baixa_epsodio(self, nome, inicio, fim):
        print(f'{nome} - {inicio} - {fim}')
        with open('episodios.txt', 'r') as f:
            linhas = f.readlines()
            for linha in linhas:
                linha = linha.replace('\n', '')
                # print(linha)
                link = linha.split(',')
                if link[0]:
                    if int(link[0]) >= int(inicio) and int(link[0]) <= int(fim):
                        print(link[1])
                        page = requests.get(link[1])
                        soup = BeautifulSoup(page.text, 'html.parser')
                        with sync_playwright() as p:
                            browser = p.firefox.launch(headless=False)
                            page = browser.new_page()
                            page.goto(link[1])
                            URL = page.content()
                            # url = links.attrs['src']
                            with open('code.txt', 'w') as z:
                                z.write(page.content())

                    # with sync_playwright() as p:
                    #     browser = p.firefox.launch(headless=False)
                    #     page = browser.new_page()
                    #     page.goto(url)
                    #     page.screenshot(path="tela_anime.png")
                    #     # URL = page.content()
                    #     # print(URL)
                    #     # with open('code.txt', 'w') as z:
                    #     #     z.write(URL)
                    #     # soup = BeautifulSoup(URL, 'html.parser')
                    #     # links = soup.find('video')
                    #     # link_down = links.attrs['src']

                    #     # r = requests.get(link_down, allow_redirects=True)
                    #     # print(f'{nome}_{link[0]}.mp4')
                    #     # open(f'nome.mp4', 'wb').write(r.content)

    def baixa_mp4(self):
        t = Funcao(window.statusbar, window.ed_nome,
                   window.ed_inicio, window.ed_fim)
        retorno = t.start()


A = Animes()

# pesquisa o anime com o nome passado
window.bt_pesquisar.clicked.connect(
    lambda: A.pesquisa_animes(window.ed_nome.text()))

# com 2 cliques no anime, pega os episodios
window.lista_animes.doubleClicked.connect(
    lambda: A.pesquisa_episodio(window.lista_animes.currentItem().text()))

# inicia o download do episodio
# window.bt_baixar_eps.clicked.connect(
#     lambda: A.baixa_epsodio(
#         window.ed_nome.text(),
#         window.ed_inicio.text(),
#         window.ed_fim.text(),
#         lista_episodios))
window.bt_baixar_eps.clicked.connect(lambda: A.baixa_epsodio(
    window.ed_nome.text(), window.ed_inicio.text(), window.ed_fim.text()))
# window.bt_baixar_eps.clicked.connect(lambda: A.baixa_mp4())

# exibe o programa
window.show()
app.exec()


# A.pesquisa_animes('naruto')
# A.pesquisa_episodio('https://animesonline.club/anime/boruto-naruto-next-generations')
# A.baixa_epsodio('https://animesonline.club/anime/boruto-naruto-next-generations/episodio/54943')
