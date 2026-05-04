from datetime import datetime
from time import sleep

import requests
from bs4 import BeautifulSoup


class PartidasScraper:
    """manipular dados de competicoes de futebol."""

    def __init__(self):
        """inicializar os objetos da classe."""
        self.soup = None
        self.equipes = []
        self.partidas = []
        self.eventos = []
        self.lista_jogadores = []
        self.estadios = []
        self.arbitros = []
        self.competicao_id = 0
        self.tipo_competicao = None
        self.temporada = None

    def __fazer_requisicao(self, url):
        """fazer uma requisicao http e retornar um objeto beautifulsoup com os dados da pagina"""
        try:
            cabecalho = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"}
            resposta = requests.get(url, headers=cabecalho)
            resposta.raise_for_status()
            conteudo = resposta.content.decode("utf8", "ignore")
            conteudo = BeautifulSoup(conteudo, "html.parser")

            print(f"requisicao realizada com sucesso!")
            return conteudo

        except requests.exceptions.RequestException as e:
            print(f"erro ao fazer requisicao para {url}: {e}")
            return None

    # implementar a rotina no app para obter os valores do layout
    def obter_competicoes(self, competicao_id, url, temporada):
        # montar url e obter pagina que sera consultada - ok
        self.competicao_id = competicao_id
        self.tipo_competicao = "copa" if "pokalwettbewerb" in url else "liga"
        self.temporada = str(int(temporada)) if competicao_id == 1 else str(int(temporada) - 1)
        url = url.replace("{ano}", self.temporada[2:])
        url = url.replace("{temporada}", self.temporada)
        self.soup = self.__fazer_requisicao(url)

    # link, competicao_id, id, situacao, arbitro_id, estadio_id, temporada, rodada, data_partida, placar, placar_pen, mandante_id, visitante_id
    def __obter_partidas(self):
        """Obtem links dos jogos do campeonato"""
        try:
            jogos_realizados = self.soup.select("div.box table tbody td.zentriert.hauptlink a.ergebnis-link")
            jogos_pendentes = self.soup.select('div.box table tbody td.zentriert.hauptlink a[title="Antevisão"]')

            tmp_link = "https://www.transfermarkt.com.br/spielbericht/index/spielbericht/"

            for jogo in jogos_realizados:
                id = jogo.get("href").split("/")[-1]
                link = f"{tmp_link}{id}"
                self.lista_partidas.append([link, self.competicao_id, id, True])

            for jogo in jogos_pendentes:
                id = jogo.get("href").split("/")[-1]
                link = f"{tmp_link}{id}"
                self.lista_partidas.append([link, self.competicao_id, id, False])

        except Exception as e:
            print(f"erro ao obter partidas: {e}")

        else:
            print(f"sucesso ao obter partidas da competicao")

        finally:
            print(f"foram obtidas {len(self.partidas)} partidas para esta competicao")

    def __obter_partidas_informacao(self):
        """obter informacoes basicas da partida, como a data e rodada"""
        try:
            informacoes = self.soup.select_one("div.sb-spieldaten p.sb-datum")
            informacoes = informacoes.get_text(strip=True).split("|")

            rodada, data = None, None

            if len(informacoes) > 0:
                rodada = informacoes[0].strip().title()
                data = informacoes[1][4:].strip()

        except (IndexError, ValueError, KeyError, TypeError) as e:
            rodada, data = None, None
            print(f"erro ao obter informacoes das partidas: {e}")

        else:
            print(f"informacoes da partida extraidas com sucesso!")

        finally:
            return rodada, data

    def __obter_partidas_estadio(self):
        """obter as informacoes do estadio e arbitro da partida."""
        informacoes = self.soup.select("p.sb-zusatzinfos a")

        estadio_id = None
        estadio = None
        arbitro_id = None
        arbitro = None

        if len(informacoes) > 0:
            estadio_id = informacoes[0].get("href").split("verein/")[1].split("/")[0]
            estadio = informacoes[0].text.strip().title()
            self.estadios.append([estadio_id, estadio])

        if len(informacoes) > 1:
            arbitro_id = informacoes[1].get("href").split("schiedsrichter/")[1].split("/")[0]
            arbitro = informacoes[1].text.strip().title()
            self.arbitros.append([arbitro_id, arbitro])

        return estadio_id, arbitro_id

    def __obter_partidas_equipes(self):
        """obter as equipes que disputaram a partida."""
        equipes = self.soup.select("div.sb-team a.sb-vereinslink")

        mandante_id = None
        visitante_id = None

        if len(equipes) > 0:
            mandante_id = equipes[0].get("href").split("verein/")[1].split("/")[0]
            visitante_id = equipes[1].get("href").split("verein/")[1].split("/")[0]

        return mandante_id, visitante_id

    def __obter_partidas_placar(self):
        """obter o placar da partida e as informacoes da disputa por penalidades."""
        placar = self.soup.select("#sb-tore div.sb-aktion-spielstand")
        placar = placar[-1].get_text(strip=True) if placar else "0:0"
        penalidades = self.soup.select("#sb-elfmeterscheissen div.sb-aktion-spielstand")
        penalidades = penalidades[-1].get_text(strip=True) if penalidades else None
        return placar, penalidades

    def __converter_minutos(self, elemento):
        """converter a posicao de um elemento em minutos, considerando as posicoes X e Y."""
        try:
            posicao = elemento["style"].replace("px", "")
            posicao_x = int((abs(int(posicao.split(" ")[1].split(";")[0])) / 36) + 1)
            posicao_y = int((abs(int(posicao.split(" ")[2].split(";")[0])) / 36) * 10)
            acrescimos = -1 if "+" in elemento.text.strip() else 0
            tempo_adicional = abs(int(elemento.text)) if acrescimos != 0 else 0
            minutos = posicao_x + posicao_y + tempo_adicional
            print(f"textoMinuto: {elemento.text.strip()}, acrescimos: {acrescimos}")

        except (IndexError, ValueError, KeyError, TypeError) as e:
            posicao_x = 0
            posicao_y = 0
            acrescimos = 0
            minutos = 0
            print(f"Erro ao calcular as posições: {e}")

        return minutos, acrescimos

    def __obter_eventos_cartoes(self):
        """Processa os eventos do jogo e armazena no banco de dados"""
        try:
            eventos = self.soup.select("#sb-karten div.sb-aktion")
            for evento in eventos:
                jogador_id = evento.select_one("div.sb-aktion-aktion a.wichtig")["href"].split("spieler/")[1].split("/")[0]
                info = evento.select_one("div.sb-aktion-aktion").find_all(string=True)[1].split(", ")
                info = info[1].strip() if len(info) > 1 else None
                equipe_id = self.mandante_id if evento.parent["class"][0] == "sb-aktion-heim" else self.visitante_id
                minutos, acrescimos = self.__converter_minutos(evento.select_one("div.sb-aktion-uhr span.sb-sprite-uhr-klein"))
                # segundo cartao amarelo gera o vermelho que anula os amarelos da partida, vermelho de forma direta mantém o amarelo anterior
                tipo = evento.select_one("div.sb-aktion-spielstand span")["class"][1]
                tipo = "CV" if tipo == "sb-rot" else "CA"
                self.eventos.append([self.item_atual[2], jogador_id, equipe_id, tipo, minutos, acrescimos, info])

                if not any(jogador_id == jogador[0] for jogador in self.lista_jogadores):
                    jogador_nome = evento.select_one("div.sb-aktion-aktion a.wichtig")["title"].strip().title()
                    jogador_url = f"https://www.transfermarkt.com.br/player/profil/spieler/{jogador_id}"
                    jogador_foto = f"https://img.a.transfermarkt.technology/portrait/header/default.jpg"
                    self.jogadores.append([jogador_url, jogador_id, jogador_nome, jogador_foto])

        except (IndexError, ValueError, KeyError, TypeError) as e:
            print(f"erro ao obter cartoes da partida: {e}")
        else:
            print(f"sucesso ao obter cartoes da partida")
        finally:
            return True

    def __obter_eventos_gols(self):
        """Obtem a lista dos jogadores que marcaram gols"""
        try:
            eventos = self.soup.select("#sb-tore div.sb-aktion")
            for evento in eventos:
                jogador_id = evento.select_one("div.sb-aktion-aktion a.wichtig").get("href").split("spieler/")[1].split("/")[0]
                info = evento.select_one("div.sb-aktion-aktion").find_all(string=True)[2].split(", ")
                info = info[1].strip() if len(info) > 1 else None
                equipe_id = self.mandante_id if evento.parent["class"][0] == "sb-aktion-heim" or (evento.parent["class"][0] == "sb-aktion-gast" and info == "Gol contra") else self.visitante_id
                minutos, acrescimos = self.__converter_minutos(evento.select_one("div.sb-aktion-uhr span.sb-sprite-uhr-klein"))
                tipo = "G"
                self.eventos.append([self.item_atual[2], jogador_id, equipe_id, tipo, minutos, acrescimos, info])

                if not any(jogador_id == jogador[0] for jogador in self.lista_jogadores):
                    jogador_nome = evento.select_one("div.sb-aktion-aktion a.wichtig")["title"].strip().title()
                    jogador_url = f"https://www.transfermarkt.com.br/player/profil/spieler/{jogador_id}"
                    jogador_foto = f"https://img.a.transfermarkt.technology/portrait/header/default.jpg"
                    self.jogadores.append([jogador_url, jogador_id, jogador_nome, jogador_foto])

        except (IndexError, ValueError, KeyError, TypeError) as e:
            print(f"erro ao obter gols da partida: {e}")
        else:
            print(f"sucesso ao obter gols da partida")
        finally:
            return True

    def __obter_eventos_assistencias(self):
        """Obtem a lista dos jogadores que deram assistencias"""
        try:
            eventos = self.soup.select("#sb-tore div.sb-aktion")
            for evento in eventos:
                div = evento.find_all("div")[3].find_all("a")
                if len(div) > 1:
                    jogador_id = div[1].get("href").split("spieler/")[1].split("/")[0]
                    info = evento.find_all("div")[3].find_all(string=True)[5].split(", ")
                    info = info[1].strip() if len(info) > 1 else None
                    equipe_id = self.mandante_id if evento.parent["class"][0] == "sb-aktion-heim" else self.visitante_id
                    minutos, acrescimos = self.__converter_minutos(evento.find("div").find("span"))
                    tipo = "A"
                    self.eventos.append([self.item_atual[2], jogador_id, equipe_id, tipo, minutos, acrescimos, info])
                    if not any(jogador_id == jogador[0] for jogador in self.lista_jogadores):
                        jogador_nome = evento.select_one("div.sb-aktion-aktion a.wichtig")["title"].strip().title()
                        jogador_url = f"https://www.transfermarkt.com.br/player/profil/spieler/{jogador_id}"
                        jogador_foto = f"https://img.a.transfermarkt.technology/portrait/header/default.jpg"
                        self.jogadores.append([jogador_url, jogador_id, jogador_nome, jogador_foto])

        except (IndexError, ValueError, KeyError, TypeError) as e:
            print(f"erro ao obter assistencias da partida: {e}")
        else:
            print(f"sucesso ao obter assistencias da partida")
        finally:
            return True

    #   https://www.transfermarkt.com.br/spielbericht/index/spielbericht/4111940
    def __obter_informacoes(self):
        """Obtem as informacoes detalhadas de um jogo e seus eventos (cartões, gols, assistências)"""
        self.soup = self.__fazer_requisicao(self.item_atual[0])
        sleep(3)
        rodada, data_partida = self.__obter_partidas_informacao()
        placar, placar_pen = self.__obter_partidas_placar()
        self.mandante_id, self.visitante_id = self.__obter_partidas_equipes()
        estadio_id, arbitro_id = self.__obter_partidas_estadio()

        self.item_atual.extend([arbitro_id, estadio_id, self.temporada, rodada, data_partida, placar, placar_pen, self.mandante_id, self.visitante_id])

        if self.item_atual[3] == True:
            print(f"Obtendo eventos do jogo realizado: {self.item_atual[2]}")
            self.db.excluir_eventos(self.item_atual[2])
            self.__obter_eventos_cartoes()
            self.__obter_eventos_gols()
            self.__obter_eventos_assistencias()

    # def __obter_jogadores_info(self):
    #     """Obtem info dos jogadores do campeonato"""
    #     jogador_id = self.item_atual[0]
    #     url = f"https://www.transfermarkt.com.br/player/profil/spieler/{self.item_atual[0]}"
    #     soup = self.__fazer_requisicao(url)
    #     data_nasc = soup.select_one("header.data-header div.data-header__info-box span").get_text(strip=True)[0:10]
    #     nacionalidade = soup.select_one("header.data-header div.data-header__info-box img").get("title").strip()
    #     nome_jogador = soup.select_one("header.data-header h1").text.split("\n")[-1].strip()
    #     foto = soup.select_one("#fotoauswahlOeffnen img")
    #     foto = foto["src"] if foto else "https://img.a.transfermarkt.technology/portrait/header/default.jpg"
    #     self.item_atual = [url, jogador_id, nome_jogador, data_nasc, nacionalidade, foto]
    #     self.db.inserir_jogadores([self.item_atual])

    #   https://www.transfermarkt.com.br/botafogo-fr_se-palmeiras/index/spielbericht/4061234
    #   https://www.transfermarkt.com.br/tournament/gesamtspielplan/wettbewerb/BRA1/saison_id/2023
    def __obter_equipes(self):
        """obtem as lista de equipes da competicao"""
        try:
            if self.tipo_competicao == "copa":
                equipes = self.soup.select('div.box table.items tr:not([class])[style] td.hauptlink a:not([class]):not([href="#"])')
            else:
                equipes = self.soup.select("div.box table:not([class]) tbody tr:not([class]) td.hauptlink a:not([class])")[:20]

            for equipe in equipes:
                id = equipe.get("href").split("verein/")[1].split("/")[0]
                nome_completo = equipe["title"].strip().title()
                nome_curto = equipe.get_text().strip().title()
                emblema = f"https://tmssl.akamaized.net//images/wappen/head/{id}.png"
                link = f"https://www.transfermarkt.com.br/team/datenfakten/verein/{id}"
                self.equipes.append([id, nome_curto, nome_completo, emblema, link])

        except (IndexError, ValueError, KeyError, TypeError) as e:
            print(f"erro ao obter equipes da competicao\n{e}")
            return False
        else:
            print(f"sucesso ao obter equipes da competicao\n")
        finally:
            return True

    # implementar a rotina no app para obter os valores do layout
    def obter_competicoes(self, competicao_id, url, temporada):
        # montar url e obter pagina que sera consultada - ok
        self.competicao_id = competicao_id
        self.tipo_competicao = "copa" if "pokalwettbewerb" in url else "liga"
        self.temporada = str(int(temporada)) if competicao_id == 1 else str(int(temporada) - 1)
        url = url.replace("{ano}", self.temporada[2:])
        url = url.replace("{temporada}", self.temporada)
        self.soup = self.__fazer_requisicao(url)

        # equipes - ok
        self.__obter_equipes()

        # cadastrar as equipes no banco de dados
        self.db.inserir_equipes(self.equipes)

        # checagem para ver se o jogo ja esta no banco de dados - {link, competicao_id, id, situacao}
        self.lista_partidas = self.db.obter_partidas(competicao_id, temporada, False)

        print(self.lista_partidas)

        if len(self.lista_partidas) == 0:
            self.__obter_partidas()

        # obter jogadores ja cadastrados no banco {link, id, nome, foto}
        self.lista_jogadores = self.db.obter_jogadores(False)

        self.jogadores = []
        self.eventos = []

        # informacoes (data, estadio, arbitro) e eventos (gols, assistencias, cartoes)
        for i, partida in enumerate(self.lista_partidas, start=1):
            print(f"{i} / {len(self.lista_partidas)}")

            if i % 20 == 0:
                print(f"{i} itens processados, pausando por 3 segundos...")
                sleep(3)

            self.item_atual = []
            self.item_atual.extend(partida)
            self.__obter_informacoes()
            self.partidas.append(self.item_atual)
            print(self.eventos)

        # inserir arbitros no banco de dados
        self.db.inserir_arbitros(self.arbitros)

        # inserir estadios no banco de dados
        self.db.inserir_estadios(self.estadios)

        # inserir novos jogadores
        self.db.inserir_jogadores(self.jogadores)

        # inserir partidas no banco de dados
        self.db.inserir_partidas(self.partidas)

        # inserir eventos da partida
        self.db.inserir_eventos(self.eventos)

        return "Finalizado!"


app = Transfermarkt()
app.obter_competicoes(1, "https://www.transfermarkt.com.br/tournament/gesamtspielplan/pokalwettbewerb/WM{ano}/saison_id/{temporada}", 2022)
