import json

with open("jogadores.json", "r", encoding="utf-8") as f:
    jogadores = json.load(f)

ids_existentes = {j["jogador_id"] for j in jogadores}

novos_jogadores = [{"jogador_id": 2, "nome": "B"}, {"jogador_id": 3, "nome": "C"}]

mapa = {j["jogador_id"]: j for j in jogadores}

for novo in novos_jogadores:
    if novo["jogador_id"] in mapa:
        mapa[novo["jogador_id"]].update(novo)

    for chave in ["nome", "idade"]:
        if chave in novo:
            mapa[chave] = novo[chave]

    else:
        jogadores.append(novo)
