# main.py

###########################################################################################
# OBTER PARTIDAS POR ARRAY #
###########################################################################################
from service.pipeline import MatchPipeline

pipeline = MatchPipeline()

tournament_id = 1
season = 0
matches = []

result = pipeline.get_matches_details_from_array(tournament_id, season, matches)
success, message = map(str, result)
if success == "False":
    print(message)

result = pipeline.merge_matches_details()
success, message = map(str, result)
if success == "False":
    print(message)
