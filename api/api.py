import collections
import json

from flask import Flask, render_template
from flask_restful import Api, Resource

from database import DbConn

# wrap the app in the api, initilizes it using restful
app = Flask(__name__, template_folder="api_template")
api = Api(app)


@app.route("/")
def index():
    return render_template("index.html")


class Transfermarkt(Resource):
    def __init__(self):
        self.db = DbConn("database.accdb")

    def get(self, competition, season):
        params_list = (
            competition,
            season,
        )

        competition_name = self.db.select_competition_name(competition)
        arr_clubs = self.db.select_competition_clubs(params_list)
        arr_players = self.db.select_competition_players(params_list)
        arr_matches = self.db.select_competition_matches(params_list)
        arr_results = self.db.select_competition_results(params_list)
        arr_events = self.db.select_competition_events(params_list)
        d = collections.OrderedDict()
        d["competition"] = competition
        d["season"] = season
        d["competition_name"] = f'"{competition_name}"'
        d["clubs"] = arr_clubs
        d["players"] = arr_players
        d["matches"] = arr_matches
        d["results"] = arr_results
        d["events"] = arr_events
        return json.dumps(d)


# parameters<type:name>
api.add_resource(Transfermarkt, "/tm/<int:competition>/<int:season>")

if __name__ == "__main__":
    app.run(debug=True)
