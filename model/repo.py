from model.db import SQLiteConnector


class DatabaseRepository:
    def __init__(self, db: SQLiteConnector):
        self.db = db

    def clear_event_staging(self):
        sql = """
        DELETE FROM tmp_events;
        """
        return self.db.execute_script(sql)

    def clear_player_staging(self):
        sql = """
        DELETE FROM tmp_players;
        """
        return self.db.execute_script(sql)

    def clear_match_staging(self):
        sql = """
        DELETE FROM tmp_infos;
        """
        return self.db.execute_script(sql)

    def clear_team_staging(self):
        sql = """
        DELETE FROM tmp_teams;
        """
        return self.db.execute_script(sql)

    def get_tournament_by_id(self, tournament_id: int):
        sql = """
        SELECT kind, code
        FROM tournaments
        WHERE id = ?;
        """
        params = (tournament_id,)
        result = self.db.get_data(sql, params, as_dict=True)
        return result[0] if result else None

    def get_all_tournaments(self):
        sql = """
        SELECT id, tournament, kind, code
        FROM tournaments
        ORDER BY tournament ASC;
        """
        result = self.db.get_data(sql, as_dict=True)
        return result if result else None

    def get_teams_without_country(self):
        sql = """
        SELECT id
        FROM teams
        WHERE id <> 0 AND country IS NULL
        ORDER BY id ASC;
        """
        result = self.db.get_data(sql, as_dict=True)
        return result if result else None

    def get_all_matches(self, tournament_id: int):
        sql = """
        SELECT *
        FROM matches
        WHERE tournament_id = ?
        ORDER BY is_played DESC, date DESC, time ASC;
        """
        params = (tournament_id,)
        result = self.db.get_data(sql, params, as_dict=True)
        return result if result else None

    def get_matches_without_details(self, tournament_id: int):
        sql = """
        SELECT id, season
        FROM matches
        WHERE is_played IS NULL
        AND tournament_id = ?
        ORDER BY id;
        """
        params = (tournament_id,)
        result = self.db.get_data(sql, params, as_dict=True)
        return result if result else None

    def get_unplayed_matches_by_tournament(self, tournament_id: int):
        sql = """
        SELECT match_id
        FROM matches
        WHERE is_played = 0 AND tournament_id = ?
        ORDER BY date DESC, time ASC;
        """
        params = (tournament_id,)
        result = self.db.get_data(sql, params, as_dict=True)
        return result if result else None

    def get_all_events(self):
        sql = """
        SELECT *
        FROM events
        ORDER BY match_id DESC, team_id ASC
        ;
        """
        result = self.db.get_data(sql, as_dict=True)
        return result if result else None

    def insert_tmp_infos(self, matches: list):
        sql = """
        INSERT INTO tmp_infos (match_id, tournament_id, season, matchday, date, time, stadium_id, stadium, referee_id, referee, is_played, home_id, home, away_id, away, home_goals, away_goals, has_penalty, home_penalty, away_penalty, home_missed, away_missed, home_yellow, home_red, away_yellow, away_red)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        params = [
            (
                m.get("match_id"),
                m.get("tournament_id"),
                m.get("season"),
                m.get("matchday"),
                m.get("date"),
                m.get("time"),
                m.get("stadium_id"),
                m.get("stadium"),
                m.get("referee_id"),
                m.get("referee"),
                m.get("is_played"),
                m.get("home_id"),
                m.get("home"),
                m.get("away_id"),
                m.get("away"),
                m.get("home_goals"),
                m.get("away_goals"),
                m.get("has_penalty"),
                m.get("home_penalty"),
                m.get("away_penalty"),
                m.get("home_missed"),
                m.get("away_missed"),
                m.get("home_yellow"),
                m.get("home_red"),
                m.get("away_yellow"),
                m.get("away_red"),
            )
            for m in matches
        ]
        return self.db.execute_query(sql, params, batch=True)

    def insert_tmp_events(self, events: list):
        sql = """
        INSERT INTO tmp_events (match_id, team_id, player_id, player, kind, history, time, extra_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """

        params = [
            (
                e.get("match_id"),
                e.get("team_id"),
                e.get("player_id"),
                e.get("player"),
                e.get("kind"),
                e.get("history"),
                e.get("time"),
                e.get("extra_time"),
            )
            for e in events
        ]
        return self.db.execute_query(sql, params, batch=True)

    def insert_tmp_teams(self, teams: list):
        params = [
            (
                t.get("team_id"),
                t.get("team"),
                t.get("country"),
                t.get("logo"),
                t.get("color"),
            )
            for t in teams
        ]

        sql = """
        INSERT INTO tmp_teams (team_id, team, country, logo, color)
        VALUES (?, ?, ?, ?, ?);
        """
        return self.db.execute_query(sql, params, batch=True)

    def insert_tmp_players(self, players: list):
        params = [
            (
                p.get("player_id"),
                p.get("player"),
                p.get("birth_date"),
                p.get("nation"),
                p.get("photo"),
            )
            for p in players
        ]

        sql = """
        INSERT INTO tmp_players (player_id, player, birth_date, nation, photo)
        VALUES (?, ?, ?, ?, ?);
        """
        return self.db.execute_query(sql, params, batch=True)

    def insert_matches(self, matches: list):
        params = [
            (
                m.get("match_id"),
                m.get("tournament_id"),
                m.get("season"),
            )
            for m in matches
        ]

        sql = """
        INSERT OR IGNORE INTO matches (id, tournament_id, season)
        VALUES (?, ?, ?)
        ;
        """
        return self.db.execute_query(sql, params, batch=True)

    def merge_matches(self):
        sql = """
        INSERT OR REPLACE INTO matches (id, tournament_id, season, stadium_id, referee_id, is_played, has_penalty, matchday, date, time)
        SELECT match_id, tournament_id, season, stadium_id, referee_id, is_played, has_penalty, matchday, date, time
        FROM tmp_infos
        WHERE match_id IS NOT NULL
        ;
        """
        return self.db.execute_script(sql)

    def merge_referees(self):
        sql = """
        INSERT OR IGNORE INTO referees (id, referee)
        SELECT referee_id, MIN(referee)
        FROM tmp_infos
        GROUP BY referee_id;
        """
        return self.db.execute_script(sql)

    def merge_stadiums(self):
        sql = """
        INSERT OR IGNORE INTO stadiums (id, stadium)
        SELECT stadium_id, MIN(stadium)
        FROM tmp_infos
        GROUP BY stadium_id;
        """
        return self.db.execute_script(sql)

    def merge_home_results(self):
        sql = """
        INSERT OR REPLACE INTO results (match_id, team_id, goal_scored, goal_conceded, penalty_scored, penalty_missed, yellow_card, red_card, match_points)
        SELECT match_id, home_id, home_goals, away_goals, home_penalty, home_missed, home_yellow, home_red,
        CASE
            WHEN has_penalty = 0 IS NULL THEN
                CASE
                    WHEN home_goals = away_goals THEN 1
                    WHEN home_goals > away_goals THEN 3
                    ELSE 0
                END
            ELSE
                CASE
                    WHEN home_penalty > away_penalty THEN 3
                    ELSE 0
                END
        END AS match_points
        FROM tmp_infos
        WHERE is_played = 1
        ;
        """
        return self.db.execute_script(sql)

    def merge_away_results(self):
        sql = """
        INSERT OR REPLACE INTO results (match_id, team_id, goal_scored, goal_conceded, penalty_scored, penalty_missed, yellow_card, red_card, match_points)
        SELECT match_id, away_id, away_goals, home_goals, away_penalty, away_missed, away_yellow, away_red,
        CASE
            WHEN has_penalty = 0 IS NULL THEN
                CASE
                    WHEN home_goals = away_goals THEN 1
                    WHEN home_goals > away_goals THEN 0
                    ELSE 3
                END
            ELSE
                CASE
                    WHEN home_penalty > away_penalty THEN 0
                    ELSE 3
                END
        END AS match_points
        FROM tmp_infos
        WHERE is_played = 1
        ;
        """
        return self.db.execute_script(sql)

    def merge_home_teams(self):
        sql = """
        INSERT OR IGNORE INTO teams (id, team)
        SELECT home_id, MIN(home)
        FROM tmp_infos
        GROUP BY home_id
        ;
        
        INSERT OR REPLACE INTO match_teams (match_id, team_id, home_away)
        SELECT DISTINCT match_id, home_id, 1
        FROM tmp_infos
        ;
        """
        return self.db.execute_script(sql)

    def merge_away_teams(self):
        sql = """
        INSERT OR IGNORE INTO teams (id, team)
        SELECT away_id, MIN(away)
        FROM tmp_infos
        GROUP BY away_id
        ;

        INSERT OR REPLACE INTO match_teams (match_id, team_id, home_away)
        SELECT DISTINCT match_id, away_id, 0
        FROM tmp_infos
        ;
        """
        return self.db.execute_script(sql)

    def update_teams(self):
        sql = """
        INSERT INTO teams (id, team, country, logo, color)
        SELECT DISTINCT team_id, team, country, logo, color
        FROM tmp_teams
        WHERE team_id IS NOT NULL
        ON CONFLICT(id) DO UPDATE SET
            country = COALESCE(excluded.country, teams.country),
            logo = COALESCE(excluded.logo, teams.logo),
            color = COALESCE(excluded.color, teams.color)
        ;
        """
        return self.db.execute_script(sql)

    def merge_events(self):
        sql = """
        INSERT OR REPLACE INTO events (match_id, team_id, player_id, time, extra_time, kind, history)
        SELECT match_id, team_id, player_id, time, extra_time, kind, history
        FROM tmp_events;        
        """
        return self.db.execute_script(sql)

    def merge_players(self):
        sql = """
        INSERT OR IGNORE INTO players (id, player)
        SELECT player_id, MIN(player)
        FROM tmp_events
        GROUP BY player_id;
        """
        return self.db.execute_script(sql)

    def get_players_without_nation(self):
        sql = """
        SELECT id
        FROM players
        WHERE id <> 0 AND nation IS NULL
        ORDER BY id ASC;
        """
        result = self.db.get_data(sql, as_dict=True)
        return result if result else None

    def update_players(self):
        sql = """
        INSERT INTO players (id, birth_date, nation, photo)
        SELECT DISTINCT player_id, birth_date, nation, photo
        FROM tmp_players
        WHERE player_id IS NOT NULL
        ON CONFLICT(id) DO UPDATE SET
            birth_date = COALESCE(excluded.birth_date, players.birth_date),
            nation = COALESCE(excluded.nation, players.nation),
            photo = COALESCE(excluded.photo, players.photo)
        ;
        """
        return self.db.execute_script(sql)

    def export_csv(self):
        sql = """
        .output C:/Users/Administrator/Desktop/events.csv
        SELECT * FROM events;
        .output stdout
        """
        return self.db.execute_script(sql)
