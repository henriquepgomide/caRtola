import json
from datetime import date
from os.path import join

import pandas as pd
import requests

data_json = requests.get("https://api.cartolafc.globo.com/atletas/mercado").json()

df_atletas = pd.DataFrame(data_json["atletas"])
df_atletas = df_atletas.join(pd.DataFrame(df_atletas.pop("scout").values.tolist()))

df_clubes = pd.DataFrame(data_json["clubes"].values())
df_clubes = df_clubes.rename(columns=dict(id="clube_id", nome="nome_clube", abreviacao="clube_abreviacao"))

df_posicoes = pd.DataFrame(data_json["posicoes"].values())
df_posicoes = df_posicoes.rename(columns=dict(id="posicao_id", nome="nome_posicao", abreviacao="posicao_abreviacao"))

df_merge = df_atletas.merge(df_clubes, how="left", on="clube_id").merge(df_posicoes, how="left", on="posicao_id")

rodada = df_merge.rodada_id[0].astype(str)
year = date.today().year
file = join("data", "01_raw", str(year), f"rodada-{rodada}.csv")

df_merge.to_csv(file, index=False)
# json.dump(data_json, open(file.replace(".csv", ".json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
