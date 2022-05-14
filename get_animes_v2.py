# compile com o comando
# venv\Scripts\pyinstaller.exe -F --console -w --upx-dir=Z:\Christian\Python\GitHub\upx-3.96-win64\upx-3.96-win64 --ico .\icone.ico --name "AnimesOnline.Club Downloader" .\get_animes_v2.py
import os
import re
from threading import Thread

import requests
from PyQt5 import uic
from PyQt5.QtWidgets import *
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import base64
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMainWindow, QApplication
from layout_animes import *
import sys

# # carrega a UI
# app = QApplication([])
# window = uic.loadUi('layout_animes.ui')
# self.frame.setVisible(False)
# self.resize(500, 200)
# self.setWindowTitle('AnimesOnline.Club by Christian2022')
# self.setStyleSheet('background-image: url("fundo.png");')


class Funcao(Thread):
    # declarar as variaveis que terão interação da funcao com a interface UI
    def __init__(self, status, nome, inicio, fim, nome_completo, botaoAbrePasta):
        # variaveis que herdam os componentes
        self.status = status
        self.inicio = inicio
        self.fim = fim
        self.nome = nome
        self.nome_completo = nome_completo
        self.botaoAbrePasta = botaoAbrePasta
        super().__init__()

    def funcaoExibir(self):
        self.botaoAbrePasta.setEnabled(False)
        # tenta criar a pasta para salvar o capitulo
        nome = str(self.nome_completo.currentItem().text()).split('/')[-1]
        nome = nome.replace('-', ' ').replace('_', ' ').replace('.',
                                                                ' ').replace('  ', ' ').replace('  ', ' ')
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
                    print(i, link)
                    nomeep = i.replace('   ', ' ')
                if link[0]:
                    if int(link[0]) >= int(self.inicio.text()) and int(link[0]) <= int(self.fim.text()):

                        ep = link[0]
                        print(ep)
                        with sync_playwright() as p:
                            self.status.showMessage(
                                'Capturando o link do video...')

                            browser = p.chromium.launch(
                                channel='chrome', headless=True)
                            page = browser.new_page()
                            # entra na pagina do anime
                            # ex: https://animesonline.club/anime/naruto-classico/episodio/2897
                            # procura o pela div com a classe Link para ai sim localizar o link codificado em base64
                            print(link[1])
                            page.goto(link[1])
                            player = page.inner_html('#Link')
                            print(player)
                            soup = BeautifulSoup(player, 'html.parser')
                            links = soup.find('a')

                            link = links.attrs['href']

                            # captura o codigo codificado para separar somente o necessario
                            b64 = link.split('=')
                            print(b64[1])
                            link = base64.b64decode(b64[1]+'==')
                            link = str(link).replace(
                                "b'http", 'http').replace("'", "")
                            print('decode '+link)
                            link = link.split('\\')[0]
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
                            open(f'Download/{nome.upper()}/{nome.upper()} {nomeep}.mp4', 'wb').write(
                                r.content)
                            self.status.showMessage('Download concluido!')
                            page.close()
        self.deletar()
        self.abrePasta()
        self.botaoAbrePasta.setEnabled(True)

    def abrePasta(self):
        # pega a pasta atual
        pasta = os.getcwd()
        # abre a pasta
        os.startfile(pasta+'\\Download')
        # abre a pasta de download
        # os.startfile(os.getcwd("Download"))

    def deletar(self):
        try:
            os.remove('animes.txt')
        except FileNotFoundError as e:
            print(e)
        try:
            os.remove('episodios.txt')
        except FileNotFoundError as e:
            print(e)
        try:
            os.remove('episodios_final.txt')
        except FileNotFoundError as e:
            print(e)
        try:
            os.remove('animes.txt')
        except FileNotFoundError as e:
            print(e)
        try:
            os.remove('conteudo.txt')
        except FileNotFoundError as e:
            print(e)
        try:
            os.remove('conteudo_final.txt')
        except FileNotFoundError as e:
            print(e)
        try:
            os.remove('html.txt')
        except FileNotFoundError as e:
            print(e)

    def run(self):
        self.funcaoExibir()


class Novo(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        super().setupUi(self)

        try:
            os.mkdir('Download')
        except Exception as e:
            pass

        self.frame.setVisible(False)

        self.baixarFundo()
        self.setWindowTitle('AnimesOnline.Club by Christian2022')
        self.label_fundo.setStyleSheet(
            "background-image: url('fundo.png'); width: 100%; height: 100%;")
        # pesquisa o anime com o nome passado
        self.bt_pesquisar.clicked.connect(
            lambda: self.pesquisa_animes(self.ed_nome.text()))

        # com 2 cliques no anime, pega os episodios
        self.lista_animes.doubleClicked.connect(
            lambda: self.pesquisaepi(self.lista_animes.currentItem().text()))

        self.bt_baixar_eps.clicked.connect(lambda: self.baixa_mp4())

        self.bt_abre_pasta.clicked.connect(self.abrePasta)

        self.ed_nome.returnPressed.connect(
            lambda: self.pesquisa_animes(self.ed_nome.text()))
        self.deletar()
        # exibe o programa
        self.move(100, 100)
        self.show()

    def baixarFundo(self):
        try:
            r = requests.get(
                'https://github.com/chriscoliveira/animes_download_py/blob/59da6d35cbb2f89e0c5c7ac6cc00dcb49bd13652/dist/fundo.png?raw=true')
            open('fundo.png', 'wb').write(r.content)
        except Exception as e:
            print(e)
            
    def abrePasta(self):
        # pega a pasta atual
        pasta = os.getcwd()
        # abre a pasta
        os.startfile(pasta+'\\Download')
        # abre a pasta de download
        # os.startfile(os.getcwd("Download"))

    def pesquisa_animes(self, nome):
        self.frame.setVisible(False)
        # self.resize(500, 200)
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
        self.lista_animes.clear()
        for i in anime:
            self.lista_animes.addItem(i)
        # for i in filme:
        #     self.lista_animes.addItem(i)

    def pesquisa_episodio(self, url):
        self.frame.setVisible(True)
        # self.resize(500, 600)

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
        self.lista_epsodios.clear()
        with open('episodios_final.txt', 'w') as f:
            cont = 0
            for tipo in tipos:
                versao = tipo.text.split('(')
                quantidade = int(versao[1][:-1])
                versao = versao[0]
                self.lista_epsodios.insertPlainText(
                    f'{versao} - {quantidade} episódios\n')
                dub = versao.split(' ')

                for i in range(quantidade):
                    nome = str(nomes[cont].text)  # .replace('ó', 'o')
                    f.write(
                        f'\n{cont}, {epsodios[cont].get("href")}, {dub[1]} {nome}')
                    self.lista_epsodios.insertPlainText(
                        f'{cont} - {nomes[i].text}\n')
                    cont += 1
        return conteudo

    def pesquisaepi(self, url):
        self.frame.setVisible(True)
        # self.resize(500, 600)

        with sync_playwright() as p:
            browser = p.chromium.launch(
                channel='chrome', headless=True)
            page = browser.new_page()
            # entra na pagina do anime
            page.goto(url)
            player = page.inner_html('#episodios')
            soup = BeautifulSoup(player, 'html.parser')
            page.close()
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
            # self.lista_epsodios.clear()
            #
            # abre o conteudo.txt
            with open('conteudo.txt', 'r', encoding='utf-8') as contxt:

                with open('episodios.txt', 'w') as f:
                    cont = 0
                    for tipo in tipos:
                        versao = tipo.text.split('(')
                        # print('versao: ', versao)
                        quantidade = int(versao[1][:-1])
                        # print('quantidade: ', quantidade)
                        versao = versao[0]
                        # print('versao[0]: ', versao)
                        # self.lista_epsodios.insertPlainText(
                        #     f'{versao} - {quantidade} episódios\n')
                        dub = versao.split(' ')

                        for i in range(quantidade):
                            nome = str(nomes[cont].text).replace('ó', 'o')
                            f.write(
                                f'{cont}, {epsodios[cont].get("href")}, {dub[1]} \n')
                            # self.lista_epsodios.insertPlainText(
                            #     f'{cont} - {nomes[i].text}\n')
                            # print(f'{cont} - {nomes[i].text}\n')
                            cont += 1

                with open('conteudo_final.txt', 'w', encoding='utf-8') as f:
                    conteudo = contxt.readlines()
                    cont = 0
                    for i in conteudo:
                        if 'Ep.' in i:
                            texto = i.split(' ')

                            try:
                                f.write(f'{cont},{texto[1]} {texto[2]}')
                                self.lista_epsodios.insertPlainText(
                                    f'{cont} - {texto[1]} {texto[2]}')
                            except:
                                f.write(f'{cont},{texto[1]},"_"')
                                self.lista_epsodios.insertPlainText(
                                    f'{cont} - {texto[1]} ')

                            cont += 1
                        else:
                            f.write(i)
                            self.lista_epsodios.insertPlainText(i)

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
                                    nomeepi = nomeepi.replace('\n', '')
                                    linha = f'{cap}, {link}, {nomeepi} {idioma} {dub}'
                                    f.write(linha.replace('   ', ' '))
                                except:
                                    # print(i)
                                    if '(' in i:
                                        idioma = i.split(' ')[1]
                                        # print(idioma)
                                    if 'TEMPORADA' in i:
                                        nomeepi = 'TEMPORADA '+i.split(' ')[1]
                                        nomeepi = nomeepi.replace('Dublado', '').replace(
                                            'Legendado', '')

    def baixa_mp4(self):
        t = Funcao(self.statusbar, self.ed_nome,
                   self.ed_inicio, self.ed_fim, self.lista_animes, self.bt_abre_pasta)
        retorno = t.start()

    def deletar(self):
        try:
            os.remove('animes.txt')
        except FileNotFoundError as e:
            print(e)
        try:
            os.remove('episodios.txt')
        except FileNotFoundError as e:
            print(e)
        try:
            os.remove('episodios_final.txt')
        except FileNotFoundError as e:
            print(e)
        try:
            os.remove('animes.txt')
        except FileNotFoundError as e:
            print(e)
        try:
            os.remove('conteudo.txt')
        except FileNotFoundError as e:
            print(e)
        try:
            os.remove('conteudo_final.txt')
        except FileNotFoundError as e:
            print(e)
        try:
            os.remove('html.txt')
        except FileNotFoundError as e:
            print(e)


# A.pesquisa_animes('naruto')
# A.pesquisa_episodio('https://animesonline.club/anime/boruto-naruto-next-generations')
# A.baixa_epsodio('https://animesonline.club/anime/boruto-naruto-next-generations/episodio/54943')
qt = QApplication(sys.argv)

novo = Novo()
novo.show()
qt.exec_()
