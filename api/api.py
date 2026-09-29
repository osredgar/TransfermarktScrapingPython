import sqlite3
from datetime import date
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR.parent / "database" / "transfermarkt.db"

app = Flask(__name__)
app.json.sort_keys = False


class InvalidParameter(ValueError):
    pass


def get_connection():
    connection = sqlite3.connect(f"{DB_PATH.as_uri()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def optional_integer(name, minimum=None, maximum=None):
    value = request.args.get(name)
    if value in (None, ""):
        return None

    try:
        number = int(value)
    except ValueError as error:
        raise InvalidParameter(f"'{name}' deve ser um numero inteiro.") from error

    if minimum is not None and number < minimum:
        raise InvalidParameter(f"'{name}' deve ser maior ou igual a {minimum}.")
    if maximum is not None and number > maximum:
        raise InvalidParameter(f"'{name}' deve ser menor ou igual a {maximum}.")

    return number


def optional_date(name):
    value = request.args.get(name)
    if value in (None, ""):
        return None

    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as error:
        raise InvalidParameter(f"'{name}' deve estar no formato AAAA-MM-DD.") from error


def get_filters():
    filters = {
        "tournament_id": optional_integer("tournament_id", minimum=1),
        "season": optional_integer("season", minimum=1),
        "team_id": optional_integer("team_id", minimum=1),
        "played": optional_integer("played", minimum=0, maximum=1),
        "date_from": optional_date("date_from"),
        "date_to": optional_date("date_to"),
    }
    filters["limit"] = optional_integer("limit", minimum=1, maximum=1000) or 100
    filters["offset"] = optional_integer("offset", minimum=0) or 0

    if filters["date_from"] and filters["date_to"] and filters["date_from"] > filters["date_to"]:
        raise InvalidParameter("'date_from' nao pode ser posterior a 'date_to'.")

    return filters


def build_match_query(filters):
    where_clauses = []
    parameters = []

    for field in ("tournament_id", "season", "played"):
        if filters[field] is not None:
            where_clauses.append(f"m.{field} = ?")
            parameters.append(filters[field])

    if filters["team_id"] is not None:
        where_clauses.append("? IN (home_relation.team_id, away_relation.team_id)")
        parameters.append(filters["team_id"])
    if filters["date_from"]:
        where_clauses.append("m.date >= ?")
        parameters.append(filters["date_from"])
    if filters["date_to"]:
        where_clauses.append("m.date <= ?")
        parameters.append(filters["date_to"])

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    joins = """
        FROM matches AS m
        JOIN tournaments AS tournament ON tournament.id = m.tournament_id
        LEFT JOIN stadiums AS stadium ON stadium.id = m.stadium_id
        LEFT JOIN referees AS referee ON referee.id = m.referee_id
        LEFT JOIN match_teams AS home_relation
            ON home_relation.match_id = m.id AND home_relation.home_away = 1
        LEFT JOIN teams AS home_team ON home_team.id = home_relation.team_id
        LEFT JOIN match_teams AS away_relation
            ON away_relation.match_id = m.id AND away_relation.home_away = 0
        LEFT JOIN teams AS away_team ON away_team.id = away_relation.team_id
        LEFT JOIN results AS home_result
            ON home_result.match_id = m.id AND home_result.team_id = home_relation.team_id
        LEFT JOIN results AS away_result
            ON away_result.match_id = m.id AND away_result.team_id = away_relation.team_id
    """
    return joins, where_sql, parameters


@app.get("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.get("/image/<path:filename>")
def image(filename):
    return send_from_directory(BASE_DIR.parent / "image", filename)


@app.get("/api/options")
def options():
    try:
        tournament_id = optional_integer("tournament_id", minimum=1)
    except InvalidParameter as error:
        return jsonify({"error": str(error)}), 400

    with get_connection() as connection:
        tournaments = connection.execute(
            "SELECT id, tournament FROM tournaments ORDER BY tournament"
        ).fetchall()
        seasons = []
        if tournament_id is not None:
            seasons = connection.execute(
                """
                SELECT DISTINCT season
                FROM matches
                WHERE tournament_id = ? AND season IS NOT NULL
                ORDER BY season DESC
                """,
                (tournament_id,),
            ).fetchall()

    return jsonify(
        {
            "tournaments": [dict(row) for row in tournaments],
            "seasons": [row["season"] for row in seasons],
        }
    )


@app.get("/api/matches")
def matches():
    try:
        filters = get_filters()
    except InvalidParameter as error:
        return jsonify({"error": str(error)}), 400

    joins, where_sql, parameters = build_match_query(filters)
    fields = """
        m.id AS match_id,
        m.tournament_id,
        tournament.tournament AS tournament,
        m.season,
        m.matchday,
        m.date,
        m.time,
        m.is_played,
        m.has_penalty,
        home_relation.team_id AS home_team_id,
        home_team.team AS home_team,
        home_result.goal_scored AS home_goals,
        home_result.penalty_scored AS home_penalties,
        away_relation.team_id AS away_team_id,
        away_team.team AS away_team,
        away_result.goal_scored AS away_goals,
        away_result.penalty_scored AS away_penalties,
        stadium.stadium,
        referee.referee
    """

    with get_connection() as connection:
        total = connection.execute(
            f"SELECT COUNT(*) {joins} {where_sql}", parameters
        ).fetchone()[0]
        rows = connection.execute(
            f"SELECT {fields} {joins} {where_sql} ORDER BY m.date DESC, m.time DESC, m.id DESC LIMIT ? OFFSET ?",
            [*parameters, filters["limit"], filters["offset"]],
        ).fetchall()
        matches_data = [dict(row) for row in rows]
        match_ids = [match["match_id"] for match in matches_data]

        events_by_match = {match_id: [] for match_id in match_ids}
        if match_ids:
            placeholders = ", ".join("?" for _ in match_ids)
            events = connection.execute(
                f"""
                SELECT
                    event.match_id,
                    event.team_id,
                    team.team,
                    event.player_id,
                    player.player,
                    event.kind,
                    event.history,
                    event.time,
                    event.extra_time
                FROM events AS event
                LEFT JOIN teams AS team ON team.id = event.team_id
                LEFT JOIN players AS player ON player.id = event.player_id
                WHERE event.match_id IN ({placeholders})
                ORDER BY event.match_id, event.time, event.extra_time, event.kind
                """,
                match_ids,
            ).fetchall()

            for event in events:
                event_data = dict(event)
                event_data.pop("match_id")
                events_by_match[event["match_id"]].append(event_data)

    for match in matches_data:
        match["events"] = events_by_match[match["match_id"]]

    response_filters = {key: value for key, value in filters.items() if value is not None}
    return jsonify(
        {
            "filters": response_filters,
            "pagination": {
                "total": total,
                "limit": filters["limit"],
                "offset": filters["offset"],
                "returned": len(rows),
            },
            "data": matches_data,
        }
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
