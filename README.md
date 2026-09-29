# About
Tool used to scraping matches data from Transfermarkt, generates a SQLite database, user can get data from this API. 

## Development
- Scrap matches from the tournament;
- Save data to a SQLite database;
- Generate data to an API for the users;
- Show basic data in a dashboard using Streamlit;

## Match query API

Start the local API from the project root:

```powershell
.\.venv\Scripts\python.exe api\api.py
```

Open `http://127.0.0.1:5000` to use the query form. It exports the displayed result as JSON.

The endpoint `GET /api/matches` accepts these optional query parameters:

- `tournament_id`
- `season`
- `team_id`
- `date_from` and `date_to` in `AAAA-MM-DD`
- `played`: `1` for played matches or `0` for unplayed matches
- `limit` from `1` to `1000`, and `offset`

Example: `http://127.0.0.1:5000/api/matches?tournament_id=1&season=2025&limit=20`
