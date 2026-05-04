CREATE TABLE IF NOT EXISTS tmp_matches (
    tournament_id TEXT,
    season INTEGER,
    match_id INTEGER,
    matchday TEXT,
    date TEXT,
    time TEXT,
    is_played INTEGER,
    home_id INTEGER,
    away_id INTEGER,
    home TEXT,
    away TEXT,
    result TEXT,
    home_goals INTEGER,
    away_goals INTEGER,
    link TEXT
);

CREATE INDEX idx_tmp_matches_tournament ON tmp_matches (tournament_id);

CREATE INDEX idx_tmp_matches_match ON tmp_matches (match_id);

CREATE INDEX idx_tmp_matches_home ON tmp_matches (home_id);

CREATE INDEX idx_tmp_matches_away ON tmp_matches (away_id);

CREATE TABLE IF NOT EXISTS tmp_matches_details (
    match_id INTEGER,
    team_id INTEGER,
    player_id INTEGER,
    player TEXT,
    kind TEXT,
    history TEXT,
    time INTEGER,
    extra_time INTEGER
);

CREATE INDEX idx_tmp_matches_details_match ON tmp_matches_details (match_id);

CREATE INDEX idx_tmp_matches_details_team ON tmp_matches_details (team_id);

CREATE INDEX idx_tmp_matches_details_player ON tmp_matches_details (player_id);

CREATE TABLE IF NOT EXISTS tournaments (
    id TEXT,
    kind TEXT,
    tournament TEXT,
    CONSTRAINT pk_tournaments PRIMARY KEY (id)
);

CREATE INDEX idx_tournaments_kind ON tournaments (kind);

CREATE TABLE IF NOT EXISTS matches (
    id INTEGER,
    tournament_id TEXT,
    season INTEGER,
    home_id INTEGER,
    away_id INTEGER,
    matchday TEXT,
    date TEXT,
    time TEXT,
    is_played INTEGER,
    link TEXT,
    CONSTRAINT pk_matches PRIMARY KEY (id),
    CONSTRAINT fk_matches_tournaments FOREIGN KEY (tournament_id) REFERENCES tournaments (id) ON DELETE CASCADE,
    CONSTRAINT fk_matches_home_clubs FOREIGN KEY (home_id) REFERENCES clubs (id) ON DELETE CASCADE,
    CONSTRAINT fk_matches_away_clubs FOREIGN KEY (away_id) REFERENCES clubs (id) ON DELETE CASCADE
);

CREATE INDEX idx_matches_tournament ON matches (tournament_id);

CREATE INDEX idx_matches_season ON matches (season);

CREATE INDEX idx_matches_tournament_season ON matches (tournament_id, season);

CREATE INDEX idx_matches_home ON matches (home_id);

CREATE INDEX idx_matches_away ON matches (away_id);

CREATE INDEX idx_matches_clubs ON matches (home_id, away_id);

CREATE INDEX idx_matches_date ON matches (date);

CREATE TABLE IF NOT EXISTS details (
    id INTEGER,
    stadium_id INTEGER,
    referee_id INTEGER,
    home_gs INTEGER,
    home_ps INTEGER,
    home_pm INTEGER,
    away_gs INTEGER,
    away_ps INTEGER,
    away_pm INTEGER,
    CONSTRAINT pk_details PRIMARY KEY (id),
    CONSTRAINT fk_details_stadiums FOREIGN KEY (stadium_id) REFERENCES stadiums (id) ON DELETE CASCADE,
    CONSTRAINT fk_details_referees FOREIGN KEY (referee_id) REFERENCES referees (id) ON DELETE CASCADE
);

CREATE INDEX idx_details_stadium ON details (stadium_id);

CREATE INDEX idx_details_referee ON details (referee_id);

CREATE TABLE IF NOT EXISTS results (
    match_id INTEGER,
    team_id INTEGER,
    goal_scored INTEGER,
    goal_conceded INTEGER,
    goal_difference INTEGER,
    points INTEGER,
    penalty_shootout INTEGER,
    yellow_card INTEGER,
    red_card INTEGER,
    CONSTRAINT pk_results PRIMARY KEY (match_id, team_id),
    CONSTRAINT fk_results_matches FOREIGN KEY (match_id) REFERENCES matches (id),
    CONSTRAINT fk_results_teams FOREIGN KEY (team_id) REFERENCES teams (id)
);

CREATE INDEX idx_results_match ON results (match_id);

CREATE INDEX idx_results_team ON teams (team_id);

CREATE TABLE IF NOT EXISTS events (
    match_id INTEGER,
    team_id INTEGER,
    player_id INTEGER,
    kind TEXT,
    history TEXT,
    time INTEGER,
    extra_time INTEGER,
    CONSTRAINT fk_events_matches FOREIGN KEY (match_id) REFERENCES matches (id),
    CONSTRAINT fk_events_teams FOREIGN KEY (team_id) REFERENCES teams (id),
    CONSTRAINT fk_events_players FOREIGN KEY (player_id) REFERENCES players (id)
);

CREATE INDEX idx_events_match ON Eventos (match_id);

CREATE INDEX idx_events_team ON Eventos (team_id);

CREATE INDEX idx_events_player ON Eventos (player_id);

CREATE INDEX idx_events_kind ON Eventos (kind);

CREATE INDEX idx_events_match_time ON Eventos (match_id, time, extra_time);

CREATE TABLE IF NOT EXISTS teams (
    id INTEGER,
    team TEXT,
    country TEXT,
    logo TEXT,
    color TEXT,
    link TEXT,
    CONSTRAINT pk_teams PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS stadiums (
    id INTEGER,
    stadium TEXT,
    CONSTRAINT pk_stadiums PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS players (
    id INTEGER,
    player TEXT,
    dob TEXT,
    nation TEXT,
    photo TEXT,
    link TEXT,
    CONSTRAINT pk_players PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS referees (
    id INTEGER,
    referee TEXT,
    CONSTRAINT pk_referees PRIMARY KEY (id)
);