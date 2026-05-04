# import json
# import os

import requests
from bs4 import BeautifulSoup


def __fetch(url: str):
    import random
    import time

    time.sleep(random.uniform(2, 5))

    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response_content = response.content.decode("utf8", "ignore")
        return BeautifulSoup(response_content, "html.parser")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching page\n{url}:\n{e}")
        return None


def __get_teams(soup: BeautifulSoup):
    home_id = away_id = home = away = None

    tags = soup.select("div.sb-team:not(.hide-for-small) a.sb-vereinslink")

    for tag in tags:
        tag_parent_class = tag.parent.get("class")

        if "sb-heim" in tag_parent_class:
            home_id = int(tag.get("href").split("/verein/")[-1].split("/")[0])
            home = tag.get_text(strip=True).title()
            continue

        if "sb-gast" in tag_parent_class:
            away_id = int(tag.get("href").split("/verein/")[-1].split("/")[0])
            away = tag.get_text(strip=True).title()
            continue

    return {"home_id": home_id, "home": home, "away_id": away_id, "away": away}


def __get_player_info(player_id: int):
    url = f"https://www.transfermarkt.com.br/player/profil/spieler/{player_id}"
    soup = __fetch(url)

    player = nation = birth_date = photo = None

    photo_tag = soup.select_one("#fotoauswahlOeffnen img")

    if photo_tag:
        photo = photo_tag.get("src").strip().lower()
        player = photo_tag.get("title").strip().title()
    else:
        photo = "https://img.a.transfermarkt.technology/portrait/header/default.jpg"

    data_table = soup.select("div.spielerdatenundfakten > div.info-table > span.info-table__content--regular")
    for row in data_table:
        row_title = row.get_text(strip=True).lower()

        if "nasc./idade" in row_title:
            birth_date = row.next_element.select_one("a").get("href").split("/datum/")[-1]
            continue

        if "nacionalidade" in row_title:
            nation = row.next_element.get_text(strip=True)
            continue

    return player_id, player, nation, birth_date, photo


def __get_informations(soup: BeautifulSoup):
    matchday = date = time = None
    div = soup.select_one("div.sb-spieldaten p.sb-datum")
    matchday = div.get_text(strip=True).split("|")[0].split("-")[0].strip().title()
    time = div.get_text(strip=True).split("|")[2].strip()

    div = soup.select_one("div.sb-spieldaten p.sb-datum a")
    date = div.get("href").split("/datum/")[-1].strip()

    stadium_id = stadium = referee_id = referee = None
    tags = soup.select("div.sb-spieldaten p.sb-zusatzinfos a")
    for tag in tags:
        link = tag.get("href")

        if "verein" in link:
            stadium_id = link.split("/verein/")[-1].split("/")[0]
            stadium = tag.get_text(strip=True).title()
            continue

        if "schiedsrichter" in link:
            referee_id = link.split("/schiedsrichter/")[-1].split("/")[0]
            referee = tag.get_text(strip=True).title()
            continue

    tag = soup.select_one("div.sb-halbzeit")
    is_played = 1 if tag else 0

    return {"matchday": matchday, "date": date, "time": time, "stadium_id": stadium_id, "stadium": stadium, "referee_id": referee_id, "referee": referee, "is_played": is_played}


def __convert_minutes(action):
    action_style = action.get("style").replace("px", "").replace(";", "").split(": ")[-1]
    action_text = action.get_text(strip=True)

    pos_x = abs(int(action_style.split(" ")[0]))
    pos_y = abs(int(action_style.split(" ")[-1]))

    time = int((pos_x / 36) + 1) + int((pos_y / 36) * 10)
    extra_time = abs(int(action_text)) if "+" in action_text else 0

    return time, extra_time


def __get_goals(soup: BeautifulSoup):
    home_goals = away_goals = result = None

    tags = soup.select_one("div#sb-tore")

    if tags is not None:
        tag = tags.select("li.sb-aktion-heim")
        home_goals = len(tag) if tag else 0

        tag = tags.select("li.sb-aktion-gast")
        away_goals = len(tag) if tag else 0

        result = f"{home_goals}:{away_goals}"

    return {"result": result, "home_goals": home_goals, "away_goals": away_goals}


def __get_penalties(soup: BeautifulSoup):
    home_penalty = home_missed = away_penalty = away_missed = None
    penalty = missed = None

    tags = soup.select_one("div#sb-elfmeterscheissen")

    if tags is not None:
        tag = tags.select("li.sb-aktion-heim span.sb-11m-tor")
        home_penalty = len(tag)

        tag = tags.select("li.sb-aktion-gast span.sb-11m-tor")
        away_penalty = len(tag)

        tag = tags.select("li.sb-aktion-gast span.sb-11m-verschossen")
        home_missed = len(tag)

        tag = tags.select("li.sb-aktion-heim span.sb-11m-verschossen")
        away_missed = len(tag)

        penalty = f"{home_penalty}:{away_penalty}"
        missed = f"{home_missed}:{away_missed}"

    return {"penalty": penalty, "missed": missed, "home_penalty": home_penalty, "away_penalty": away_penalty, "home_missed": home_missed, "away_missed": away_missed}


def __get_cards(soup: BeautifulSoup):
    home_yellow = away_yellow = home_red = away_red = None
    red_card = yellow_card = None

    tags = soup.select_one("div#sb-karten")

    if tags is not None:
        home_yellow = away_yellow = home_red = away_red = 0

        tag = tags.select("li.sb-aktion-heim span.sb-gelb")
        home_yellow += len(tag) if tag else 0

        tag = tags.select("li.sb-aktion-heim span.sb-rot")
        home_red += len(tag) if tag else 0

        tag = tags.select("li.sb-aktion-heim span.sb-gelbrot")
        home_yellow += len(tag) if tag else 0
        home_red += len(tag) if tag else 0

        tag = tags.select("li.sb-aktion-gast span.sb-gelb")
        away_yellow += len(tag) if tag else 0

        tag = tags.select("li.sb-aktion-gast span.sb-srot")
        away_red += len(tag) if tag else 0

        tag = tags.select("li.sb-aktion-gast span.sb-gelbrot")
        away_yellow += len(tag) if tag else 0
        away_red += len(tag) if tag else 0

        yellow_card = f"{home_yellow}:{away_yellow}"
        red_card = f"{home_red}:{away_red}"

    return {"yellow_card": yellow_card, "red_card": red_card, "home_yellow": home_yellow, "home_red": home_red, "away_yellow": away_yellow, "away_red": away_red}


def __get_goals_details(soup: BeautifulSoup, match_id: int, home_id: int, away_id: int):
    events = []

    rows = soup.select("div#sb-tore div.sb-aktion")

    if rows is None:
        return events

    for row in rows:
        # row_parent_class = row.parent.get("class")

        team_id = player_id = 0
        player = time = extra_time = history = kind = None

        # time
        action = row.select_one("div.sb-aktion-uhr span")
        time, extra_time = __convert_minutes(action)

        # team
        team_id = row.select_one("div.sb-aktion-wappen a").get("href").split("/verein/")[-1].split("/")[0]

        # goals and assists
        actions = row.select("div.sb-aktion-aktion a")

        for action in actions:
            history_text = action.next_sibling.get_text(strip=True).lower()
            player_id = int(action.get("href").split("/spieler/")[-1].split("/")[0])
            player = action.get_text(strip=True).title()
            history = history_text.split(", ")[-2].strip()
            history = None if "competição" in history else history.title()
            kind = "Gol" if "gol" in history_text else "Assistência"

            if "gol contra" in history_text.lower():
                events.append({"match_id": match_id, "team_id": team_id, "player_id": 0, "player": "Gol Contra", "kind": kind, "history": "Gol contra", "time": time, "extra_time": extra_time})

                team_id = away_id if team_id == home_id else home_id

                events.append({"match_id": match_id, "team_id": team_id, "player_id": player_id, "player": player, "kind": "Gol Contra", "history": None, "time": time, "extra_time": extra_time})

                break

            else:
                events.append({"match_id": match_id, "team_id": team_id, "player_id": player_id, "player": player, "kind": kind, "history": history, "time": time, "extra_time": extra_time})

                if "pênalti" in history_text.lower():
                    break

    return events


def __get_cards_details(soup: BeautifulSoup, match_id: int):
    events = []

    rows = soup.select("div#sb-karten div.sb-aktion")

    if rows is None:
        return events

    for row in rows:
        # row_parent_class = row.parent.get("class")

        team_id = player_id = 0
        player = time = extra_time = history = kind = None

        # time
        action = row.select_one("div.sb-aktion-uhr span")
        time, extra_time = __convert_minutes(action)

        # team
        team_id = row.select_one("div.sb-aktion-wappen a").get("href").split("/verein/")[-1].split("/")[0]

        # player
        action = row.select_one("div.sb-aktion-aktion a")
        player_id = action.get("href").split("/spieler/")[-1].split("/")[0]
        player = action.get_text(strip=True).title()

        history_text = action.parent.get_text(strip=True).lower()
        if ", " in history_text:
            history = history_text.split(", ")[-1].strip()
            history = None if "cartão" in history else history.capitalize()

        # cards
        action = row.select_one("div.sb-aktion-spielstand span")
        action_class = action.get("class")

        if "sb-rot" in action_class:
            kind = "Cartão Vermelho"

            events.append({"team_id": team_id, "player_id": player_id, "player": player, "kind": kind, "history": history, "time": time, "extra_time": extra_time})

            continue

        elif "sb-gelb" in action_class:
            kind = "Cartão Amarelo"

            events.append({"match_id": match_id, "team_id": team_id, "player_id": player_id, "player": player, "kind": kind, "history": history, "time": time, "extra_time": extra_time})

            continue

        elif "sb-gelbrot" in action_class:
            kind = "Cartão Amarelo"

            events.append({"team_id": team_id, "player_id": player_id, "player": player, "kind": kind, "history": history, "time": time, "extra_time": extra_time})

            kind = "Cartão Vermelho"

            events.append({"team_id": team_id, "player_id": player_id, "player": player, "kind": kind, "history": history, "time": time, "extra_time": extra_time})

            continue

    return events


def get_match_details(match_id: int, tournament_id: int, season: int):
    match_url = f"https://www.transfermarkt.com.br/spielbericht/index/spielbericht/{match_id}"
    soup = __fetch(match_url)

    curr_match = {"info": [], "events": []}

    if not soup:
        return curr_match

    tmp_data = {"match_id": match_id, "tournament_id": tournament_id, "season": season}

    informations = __get_informations(soup)
    tmp_data.update(informations)

    teams = __get_teams(soup)
    tmp_data.update(teams)

    goals = __get_goals(soup)
    tmp_data.update(goals)

    penalties = __get_penalties(soup)
    tmp_data.update(penalties)

    cards = __get_cards(soup)
    tmp_data.update(cards)

    home_id = tmp_data["home_id"]
    away_id = tmp_data["away_id"]
    is_played = tmp_data["is_played"]

    curr_match["info"].append(tmp_data)

    if is_played != 0:
        goals_details = __get_goals_details(soup, match_id, home_id, away_id)
        curr_match["events"].extend(goals_details)

        cards_details = __get_cards_details(soup, match_id)
        curr_match["events"].extend(cards_details)

    return curr_match


def get_tournament_matches(kind: str, code: str, tournament_id: int, season: int):
    base_url = f"https://www.transfermarkt.com.br/tournament/gesamtspielplan/{kind}/{code}/saison_id/{season}"

    soup = __fetch(base_url)

    matches = []

    if soup is None:
        return matches

    rows = soup.select("div.box table tbody td.zentriert.hauptlink a")

    for row in rows:
        match_id = int(row.get("href").split("/spielbericht/")[-1])
        curr_match = {"match_id": match_id, "tournament_id": tournament_id, "season": season + 1}
        matches.append(curr_match)

    return matches


def get_player_info(player_id: int):
    player = nation = birth_date = photo = None

    url = f"https://www.transfermarkt.com.br/player/profil/spieler/{player_id}"

    soup = __fetch(url)

    if soup is None:
        return None

    tag = soup.select_one("header h1 strong")
    if tag:
        last_name = tag.get_text(strip=True).title()
        first_name = tag.previous_sibling.get_text(strip=True).title()
        player = " ".join([first_name, last_name]).strip().title()

    tag = soup.select_one("#fotoauswahlOeffnen img")
    if tag:
        photo = tag.get("src").strip().lower()
        player = tag.get("title").strip().title()

    data_table = soup.select("div.spielerdatenundfakten > div.info-table > span.info-table__content--regular")
    for row in data_table:
        row_title = row.get_text(strip=True).lower()
        print(row_title)
        if "nasc./idade" in row_title:
            birth_date = row.find_next_sibling().select_one("a").get("href").split("/datum/")[-1]
            continue

        if "nacionalidade" in row_title:
            nation = row.find_next_sibling().select_one("img").get("title").strip().title()
            break

    return [
        {
            "player_id": player_id,
            "player": player,
            "nation": nation,
            "birth_date": birth_date,
            "photo": photo,
        }
    ]


def get_team_info(team_id):
    url = f"https://www.transfermarkt.com.br/team/datenfakten/verein/{team_id}"
    soup = __fetch(url)

    team = country = logo = None
    color = "#ffffff"

    if soup is None:
        return None

    logo = f"https://tmssl.akamaized.net/images/wappen/big/{team_id}.png"

    tag = soup.select_one("header h1")
    if tag:
        team = tag.get_text(strip=True).strip().title()

    tag = soup.select_one("span.data-header__content img.flaggenrahmen")
    if tag:
        country = tag.get("title").strip().title()

    tag = soup.select_one("table.profilheader p.vereinsfarbe span")
    if tag:
        color = tag.get("style").replace(";", "").split(":")[-1].strip().lower()

    return [
        {
            "team_id": team_id,
            "team": team,
            "country": country,
            "color": color,
            "logo": logo,
        }
    ]


PLAYER = get_player_info(1125720)
print(PLAYER)

# TEAM = get_team_info(20)
# print(TEAM)

# ####################################################################################################

# penalty_shootout = "4111940"
# penalty_missed = "4061234"
# own_goal = "4810955"
# second_yellow = "987570"

# print("get_tournament_matches...")
# matches = get_tournament_matches("pokalwettbewerb", "FIWC", 2001)
# matches_infos = []
# i = 0

# for match in matches:
#     match_id = match["match_id"]
#     print(f"get_match_details... {match_id, 1, 2002}")
#     match_history = get_match_details(match_id, 1, 2002)
#     matches_infos.append(match_history)
#     i += 1

#     if i == 2:
#         break


# # resultado = [obj for obj in lista if obj.get("teste") is True]
# # resultado = [obj for obj in lista if obj.get("tipo") == 5 and obj.get("teste") is True]


# # caminho da área de trabalho
# user_desktop = os.path.join(os.path.expanduser("~"), "Desktop")
# output_file = os.path.join(user_desktop, "matches_infos.json")

# if len(matches_infos) != 0:
#     with open(output_file, "w", encoding="utf-8") as f:
#         json.dump(matches_infos, f, indent=2, ensure_ascii=False)

#     print(f"JSON path: {output_file}")
# else:
#     print(f"Error scraping the page: {output_file}")
