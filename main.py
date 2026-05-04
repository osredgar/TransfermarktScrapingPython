# main.py

# from model.db import SQLiteConnector
# from model.repo import DatabaseRepository

# db = SQLiteConnector()
# database = DatabaseRepository(db)
# database.export_csv()

# from service.pipeline import MatchPipeline

# pipeline = MatchPipeline()

# tournament_id = 1
# season = 1990

# result = pipeline.get_matches_from_tournament_season(tournament_id, season)

# success, message = map(str, result)
# if success == "False":
#     print(message)

# result = pipeline.get_matches_details(tournament_id)
# success, message = map(str, result)
# if success == "False":
#     print(message)

# result = pipeline.merge_matches_details()
# success, message = map(str, result)
# if success == "False":
#     print(message)

###########################################################################################
# OBTER PARTIDAS POR ARRAY #
###########################################################################################
# tournament_id = 1
# season = 1990
# matches = [928034]

# result = pipeline.get_matches_details_from_array(tournament_id, season, matches)
# success, message = map(str, result)
# if success == "False":
#     print(message)

# result = pipeline.merge_matches_details()
# success, message = map(str, result)
# if success == "False":
#     print(message)
