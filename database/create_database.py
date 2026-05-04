import sqlite3

conn = sqlite3.connect(r"database/transfermarkt.db")

cursor = conn.cursor()
cursor.execute("PRAGMA journal_mode = WAL;")
cursor.execute("PRAGMA synchronous = NORMAL;")
cursor.execute("PRAGMA foreign_keys = ON;")


print("Creating table: tournaments")
cursor.executescript(
    """
    CREATE TABLE IF NOT EXISTS tournaments
    (
        id INTEGER,
        tournament TEXT,
        code TEXT,
        kind TEXT,
        CONSTRAINT pk_tournaments PRIMARY KEY (id)
    );

    CREATE INDEX idx_tournaments_kind ON tournaments (kind);

    INSERT OR IGNORE INTO tournaments (id, code, kind, tournament) VALUES
    (1, "FIWC", "pokalwettbewerb", "FIFA World Cup"),
    (2, "CLI", "pokalwettbewerb", "Conmebol Libertadores"),
    (3, "CL", "pokalwettbewerb", "UEFA Champions League"),
    (4, "ACLE", "pokalwettbewerb", "AFC Champions League"),
    (5, "BRA1", "wettbewerb", "Brasileirao Serie A"),
    (6, "GB1", "wettbewerb", "English Premier League"),
    (7, "FR1", "wettbewerb", "Ligue 1"),
    (8, "ES1", "wettbewerb", "LaLiga"),
    (9, "L1", "wettbewerb", "Bundesliga"),
    (10, "IT1", "wettbewerb", "Serie A"),
    (11, "MLS1", "wettbewerb", "Major League Soccer"),
    (12, "NL1", "wettbewerb", "Eredivisie"),
    (13, "PO1", "wettbewerb", "Liga Portugal"),
    (14, "TR1", "wettbewerb", "Super Lig"),
    (15, "SA1", "wettbewerb", "Saudi Pro League");
    """
)

print("Creating table: tmp_infos")
cursor.executescript(
    """
    CREATE TABLE IF NOT EXISTS tmp_infos
    (
        match_id INTEGER,
        tournament_id INTEGER,
        season INTEGER,
        matchday TEXT,
        date TEXT,
        time TEXT,
        stadium_id INTEGER,
        stadium TEXT,
        referee_id INTEGER,
        referee TEXT,
        is_played INTEGER,
        home_id INTEGER,
        home TEXT,
        away_id INTEGER,
        away TEXT,
        home_goals INTEGER,
        away_goals INTEGER,
        has_penalty INTEGER,
        home_penalty INTEGER,
        away_penalty INTEGER,
        home_missed INTEGER,
        away_missed INTEGER,
        home_yellow INTEGER,
        home_red INTEGER,
        away_yellow INTEGER,
        away_red INTEGER
    );
    """
)

print("Creating table: tmp_events")
cursor.executescript(
    """
    CREATE TABLE IF NOT EXISTS tmp_events
    (
        match_id INTEGER,
        team_id INTEGER,
        player_id INTEGER,
        player TEXT,
        kind TEXT,
        history TEXT,
        time INTEGER,
        extra_time INTEGER
    )
    """
)

print("Creating table: referees")
cursor.executescript(
    """
    CREATE TABLE IF NOT EXISTS referees
    (
        id INTEGER,
        referee TEXT,
        CONSTRAINT pk_referees PRIMARY KEY (id)
    );
    """
)

print("Creating table: players")
cursor.executescript(
    """
    CREATE TABLE IF NOT EXISTS players
    (
        id INTEGER,
        player TEXT,
        CONSTRAINT pk_players PRIMARY KEY (id)
    );
    """
)

print("Creating table: stadiums")
cursor.executescript(
    """
    CREATE TABLE IF NOT EXISTS stadiums
    (
        id INTEGER,
        stadium TEXT,
        CONSTRAINT pk_stadiums PRIMARY KEY (id)
    );
    """
)

print("Creating table: teams")
cursor.executescript(
    """
    CREATE TABLE IF NOT EXISTS teams
    (
        id INTEGER,
        team TEXT,
        CONSTRAINT pk_teams PRIMARY KEY (id)
    );
    """
)

print("Creating table: matches")
cursor.executescript(
    """
    CREATE TABLE IF NOT EXISTS matches
    (
        id INTEGER,
        tournament_id INTEGER,
        stadium_id INTEGER,
        referee_id INTEGER,
        is_played INTEGER,
        has_penalty INTEGER,
        season INTEGER,
        matchday TEXT,
        date TEXT,
        time TEXT,
        CONSTRAINT pk_matches PRIMARY KEY (id),
        CONSTRAINT fk_matches_tournament_id FOREIGN KEY (tournament_id) REFERENCES tournaments (id) ON DELETE CASCADE,
        CONSTRAINT fk_matches_stadium_id FOREIGN KEY (stadium_id) REFERENCES stadiums (id) ON DELETE CASCADE,
        CONSTRAINT fk_matches_referee_id FOREIGN KEY (referee_id) REFERENCES referees (id) ON DELETE CASCADE
    );

    CREATE INDEX idx_matches_tournament ON matches (tournament_id);
    CREATE INDEX idx_matches_season ON matches (season);
    CREATE INDEX idx_matches_tournament_season ON matches (tournament_id, season);
    CREATE INDEX idx_matches_date_time ON matches (date, time);
    CREATE INDEX idx_matches_stadium ON matches (stadium_id);
    CREATE INDEX idx_matches_referee ON matches (referee_id);
    CREATE INDEX idx_matches_played ON matches (is_played);
    CREATE INDEX idx_matches_penalty ON matches (has_penalty);
    """
)

print("Creating table: match_teams")
cursor.executescript(
    """
    CREATE TABLE IF NOT EXISTS match_teams
    (
        match_id INTEGER,
        team_id INTEGER,
        home_away INTEGER,
        CONSTRAINT pk_match_teams PRIMARY KEY (match_id, team_id),
        CONSTRAINT fk_match_teams_match_id FOREIGN KEY (match_id) REFERENCES matches (id) ON DELETE CASCADE,
        CONSTRAINT fk_match_teams_team_id FOREIGN KEY (team_id) REFERENCES teams (id) ON DELETE CASCADE
    );

    CREATE INDEX idx_match_teams_match ON match_teams (match_id);
    CREATE INDEX idx_match_teams_team ON match_teams (team_id);
    CREATE INDEX idx_match_teams_home_away ON match_teams (home_away);
    """
)

print("Creating table: results")
cursor.executescript(
    """
    CREATE TABLE IF NOT EXISTS results
    (
        match_id INTEGER,
        team_id INTEGER,
        goal_scored INTEGER,
        goal_conceded INTEGER,
        penalty_scored INTEGER,
        penalty_missed INTEGER,
        match_points INTEGER,
        yellow_card INTEGER,
        red_card INTEGER,
        CONSTRAINT pk_results PRIMARY KEY (match_id, team_id),
        CONSTRAINT fk_results_match_id FOREIGN KEY (match_id) REFERENCES matches (id) ON DELETE CASCADE,
        CONSTRAINT fk_results_team_id FOREIGN KEY (team_id) REFERENCES teams (id) ON DELETE CASCADE
    );

    CREATE INDEX idx_results_match ON results (match_id);
    CREATE INDEX idx_results_team ON results (team_id);
    """
)

print("Creating table: events")
cursor.executescript(
    """
    CREATE TABLE IF NOT EXISTS events
    (
        match_id INTEGER,
        team_id INTEGER,
        player_id INTEGER,
        time INTEGER,
        extra_time INTEGER,
        kind TEXT,
        history TEXT,
        CONSTRAINT pk_events PRIMARY KEY (match_id, team_id, player_id, kind, time, extra_time),
        CONSTRAINT fk_events_match_id FOREIGN KEY (match_id) REFERENCES matches (id) ON DELETE CASCADE,
        CONSTRAINT fk_events_team_id FOREIGN KEY (team_id) REFERENCES teams (id) ON DELETE CASCADE,
        CONSTRAINT fk_events_player_id FOREIGN KEY (player_id) REFERENCES players (id) ON DELETE CASCADE
    );

    CREATE INDEX idx_events_match ON events (match_id);
    CREATE INDEX idx_events_team ON events (team_id);
    CREATE INDEX idx_events_player ON events (player_id);
    CREATE INDEX idx_events_kind ON events (kind);
    CREATE INDEX idx_events_match_time ON events (match_id, time, extra_time);
    """
)

# Confirmar as mudanças
conn.commit()

# Fechar a conexão
conn.close()

print("Banco de dados e tabela criados com sucesso!")
