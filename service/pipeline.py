# app/service/pipeline.py

from model.db import SQLiteConnector
from model.repo import DatabaseRepository
from service.scraper import MatchScraper


class MatchPipeline:
    def __init__(self):
        self.db = SQLiteConnector()

        # repositories
        self.repo = DatabaseRepository(self.db)

        # scraper
        self.scraper = MatchScraper()

    def get_matches_from_tournament_season(self, tournament_id: int, season: int):
        tournament = self.repo.get_tournament_by_id(tournament_id)

        if not tournament:
            return {"success": False, "message": f"Invalid tournament_id: {tournament_id}"}

        tournament_kind = tournament["kind"]
        tournament_code = tournament["code"]

        print("## get_tournament_matches ##")
        matches = self.scraper.get_tournament_matches(tournament_kind, tournament_code, tournament_id, season)

        if not matches:
            return {"success": False, "message": f"Not found matches pages for the tournament_id: {tournament_id}"}

        print("## insert_matches ##")
        self.repo.insert_matches(matches)

        return {"success": True, "message": f"{len(matches)} matches found"}

    def get_matches_details(self, tournament_id: int):
        matches = self.repo.get_matches_without_details(tournament_id)
        # matches = [
        #     936051,
        #     936658,
        #     936659,
        #     936663,
        #     936665,
        #     936684,
        #     936696,
        #     987522,
        #     987533,
        #     31199,
        #     49320,
        #     49336,
        #     53490,
        #     986787,
        #     986796,
        #     2384328,
        #     2384337,
        #     2384338,
        #     2384325,
        #     2462532,
        #     2977689,
        #     2977695,
        #     2977702,
        #     2977725,
        #     2977685,
        #     2977687,
        #     2977718,
        #     2977712,
        #     2977724,
        #     3057976,
        #     3062384,
        #     3072773,
        #     3788894,
        #     3970579,
        # ]

        if not matches:
            return {"success": False, "message": f"All matches for tournament_id: {tournament_id} already have details"}

        print("### clear_staging ###")
        self.repo.clear_match_staging()
        self.repo.clear_event_staging()

        m = 0
        m_qty = len(matches)

        for match in matches:
            m += 1
            match_id = match["id"]
            season = match["season"]

            print(f"### get_match_details {match_id} - {m} from {m_qty} ###")

            curr_match_data = self.scraper.get_match_details(match_id, tournament_id, season)

            info = curr_match_data["info"]
            events = curr_match_data["events"]

            if info:
                self.repo.insert_tmp_infos(info)

            if events:
                self.repo.insert_tmp_events(events)

        return {"success": True, "message": "Matches details are all set"}

    def merge_matches_details(self):
        print("### merge_teams ###")
        self.repo.merge_home_teams()
        self.repo.merge_away_teams()

        print("### merge_referees ###")
        self.repo.merge_referees()

        print("### merge_stadiums ###")
        self.repo.merge_stadiums()

        print("### merge_matches ###")
        self.repo.merge_matches()

        print("### merge_results ###")
        self.repo.merge_home_results()
        self.repo.merge_away_results()

        print("### merge_players ###")
        self.repo.merge_players()

        print("### merge_events ###")
        self.repo.merge_events()

        print("### clear_staging ###")
        self.repo.clear_match_staging()
        self.repo.clear_event_staging()

        return {"success": True, "message": "Merged matches data"}

    def get_team_details(self):
        teams = self.repo.get_teams_without_country()

        t = 0
        t_qty = len(teams)

        print("### clear_team_staging ###")
        self.repo.clear_team_staging()

        for team in teams:
            t += 1
            team_id = team["id"]

            print(f"### get_team_info: {team_id} - {t} from {t_qty}###")
            curr_team_details = self.scraper.get_team_info(team_id)

            if curr_team_details is None:
                break

            print("### insert_tmp_teams ###")
            self.repo.insert_tmp_teams(curr_team_details)

        print("### update_teams ###")
        self.repo.update_teams()

        print("### clear_team_staging ###")
        self.repo.clear_team_staging()

    def get_player_details(self):
        players = self.repo.get_players_without_nation()

        p = 0
        p_qty = len(players)

        print("### clear_player_staging ###")
        self.repo.clear_player_staging()

        for player in players:
            p += 1
            player_id = player["id"]

            print(f"### get_player_info: {player_id} - {p} from {p_qty}###")
            curr_player_details = self.scraper.get_player_info(player_id)

            if curr_player_details is None:
                break

            print("### insert_tmp_players ###")
            self.repo.insert_tmp_players(curr_player_details)

        print("### update_players ###")
        self.repo.update_players()

        print("### clear_player_staging ###")
        self.repo.clear_player_staging()

    def tmp_delete_column(self):
        sql = """ALTER TABLE matches DROP COLUMN confrontation;"""
        self.db.execute_query(sql)

    def get_matches_details_from_array(self, tournament_id: int, season: int, matches: object):
        if not matches:
            return {"success": False, "message": f"All matches for tournament_id: {tournament_id} already have details"}

        print("### clear_staging ###")
        self.repo.clear_match_staging()
        self.repo.clear_event_staging()

        m = 0
        m_qty = len(matches)

        for match in matches:
            m += 1

            print(f"### get_match_details {match} - {m} from {m_qty} ###")

            curr_match_data = self.scraper.get_match_details(match, tournament_id, season)

            info = curr_match_data["info"]
            events = curr_match_data["events"]

            if info:
                self.repo.insert_tmp_infos(info)

            if events:
                self.repo.insert_tmp_events(events)

        return {"success": True, "message": "Matches details are all set"}
