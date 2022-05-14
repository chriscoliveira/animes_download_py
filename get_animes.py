import os
import re
from threading import Thread

import requests
from PyQt5 import uic
from PyQt5.QtWidgets import *
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# carrega a UI
app = QApplication([])
window = uic.loadUi('layout_animes.ui')
window.frame.setVisible(False)
window.resize(500, 200)
window.setWindowTitle('AnimesOnline.Club by Christian2022')
# window.setStyleSheet('background-image: url("fundo.png");')


def deletar():
    try:
        os.remove('animes.txt')
        os.remove('episodios.txt')
        os.remove('episodios_final.txt')
        os.remove('animes.txt')
        os.remove('conteudo.txt')
        os.remove('conteudo_final.txt')
    except FileNotFoundError:
        pass


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
        nome = str(self.nome_completo.currentItem().text()).split('/')[-1]
        try:
            os.mkdir('Download')
            self.status.showMessage('Pasta Download criada com sucesso!')
        except Exception as e:
            pass
        try:
            os.mkdir('Download/' + str(nome).upper())
            self.status.showMessage(f'Pasta {nome} criada com sucesso!')
        except Exception as e:
            pass

        self.status.showMessage('')
        with open('episodios_final.txt', 'r', encoding='utf-8') as f:
            linhas = f.readlines()
            for linha in linhas:
                linha = linha.replace('\n', '')
                # print(linha)
                link = linha.split(',')
                for i in link:
                    print(i)
                    nomeep = i.replace('   ', ' ')
                if link[0]:
                    if int(link[0]) >= int(self.inicio.text()) and int(link[0]) <= int(self.fim.text()):
                        ep = link[0]
                        with sync_playwright() as p:
                            self.status.showMessage(
                                'Capturando o link do video...')

                            browser = p.chromium.launch(
                                channel='chrome', headless=True)
                            page = browser.new_page()
                            # entra na pagina do anime
                            page.goto(link[1])
                            player = page.inner_html('#player-video')
                            with open('html.txt', 'w', encoding='utf-8') as f:
                                f.write(player)
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
                            r = requests.get(
                                link_down, allow_redirects=True)
                            print(f'{self.nome.text()}_{nomeep}.mp4')
                            self.status.showMessage(
                                f'baixando {nome}_{nomeep}.mp4')
                            open(f'Download/{nome}/{nome}_{nomeep}.mp4', 'wb').write(
                                r.content)
                            self.status.showMessage('Download concluido!')
        deletar()

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
        with open('episodios_final.txt', 'w') as f:
            cont = 0
            for tipo in tipos:
                versao = tipo.text.split('(')
                quantidade = int(versao[1][:-1])
                versao = versao[0]
                window.lista_epsodios.insertPlainText(
                    f'{versao} - {quantidade} episódios\n')
                dub = versao.split(' ')

                for i in range(quantidade):
                    nome = str(nomes[cont].text)  # .replace('ó', 'o')
                    f.write(
                        f'\n{cont}, {epsodios[cont].get("href")}, {dub[1]} {nome}')
                    window.lista_epsodios.insertPlainText(
                        f'{cont} - {nomes[i].text}\n')
                    cont += 1
        return conteudo

    def pesquisaepi(self, url):
        window.frame.setVisible(True)
        window.resize(500, 600)

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

                with open('episodios.txt', 'w') as f:
                    cont = 0
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
                                f'{cont}, {epsodios[cont].get("href")}, {dub[1]} \n')
                            # window.lista_epsodios.insertPlainText(
                            #     f'{cont} - {nomes[i].text}\n')
                            print(f'{cont} - {nomes[i].text}\n')
                            cont += 1

                with open('conteudo_final.txt', 'w', encoding='utf-8') as f:
                    conteudo = contxt.readlines()
                    cont = 0
                    for i in conteudo:
                        if 'Ep.' in i:
                            f.write(f'{cont},{i}')
                            window.lista_epsodios.insertPlainText(
                                f'{cont} - {i}')
                            cont += 1
                        else:
                            f.write(i)
                            window.lista_epsodios.insertPlainText(i)

                # junta os 2 txt
                with open('episodios.txt', 'r') as eps:
                    with open('conteudo_final.txt', 'r') as cont:
                        with open('episodios_final.txt', 'w') as f:
                            conteudo_total = cont.readlines()
                            epsodios = eps.readlines()
                            nomeepi = ""
                            idioma = ""
                            for i in conteudo_total:

                                try:
                                    cap = int(i.split(',')[0])
                                    texto = epsodios[cap].split(',')
                                    # print(texto)
                                    link = texto[1]
                                    tipo = texto[2]
                                    # , tipo, sep='|')
                                    dub = i.split(',')[1]
                                    numerospi = dub.split(' ')[0]
                                    linha = f'{cap}, {link}, {nomeepi} {idioma} {dub}'
                                    f.write(linha.replace('   ', ' '))
                                except:
                                    print(i)
                                    if '(' in i:
                                        idioma = i.split(' ')[1]
                                        print(idioma)
                                    if 'TEMPORADA' in i:
                                        nomeepi = 'TEMPORADA '+i.split(' ')[1]
                                        nomeepi = nomeepi.replace('Dublado', '').replace(
                                            'Legendado', '')

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
    lambda: A.pesquisaepi(window.lista_animes.currentItem().text()))

window.bt_baixar_eps.clicked.connect(lambda: A.baixa_mp4())

deletar()
# exibe o programa
window.move(100, 100)
window.show()
app.exec()

# A.pesquisa_animes('naruto')
# A.pesquisa_episodio('https://animesonline.club/anime/boruto-naruto-next-generations')
# A.baixa_epsodio('https://animesonline.club/anime/boruto-naruto-next-generations/episodio/54943')
# https://blog.ahnoticias.com/noticia.php?token=aHR0cHM6Ly9hbmltZXNvbmxpbmUuY2x1Yi9wbGF5ZXIvMzAvSkVTTVNUQlFBSg==&origin=aHR0cHM6Ly9hbmltZXNvbmxpbmUuY2x1Yi9hbmltZS9uYXJ1dG8tc2hpcHB1ZGVuL2VwaXNvZGlvLzM2MzQ=
