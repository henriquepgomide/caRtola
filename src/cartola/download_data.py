import json
from datetime import date
from os.path import join

import pandas as pd
import requests

data_json = requests.get("https://api.cartolafc.globo.com/atletas/mercado").json()

df_atletas = pd.DataFrame(data_json["atletas"])
df_atletas = df_atletas.join(pd.DataFrame(df_atletas.pop("scout").values.tolist()))
df_atletas = df_atletas.rename(columns={col: f"atletas.{col}" if col.islower() else col for col in df_atletas.columns})
df_atletas = df_atletas.drop(columns="atletas.gato_mestre")

df_clubes = pd.DataFrame(data_json["clubes"].values())
df_clubes = df_clubes.rename(columns=dict(id="atletas.clube_id", nome="atletas.clube.id.full.name"))
df_clubes = df_clubes[["atletas.clube_id", "atletas.clube.id.full.name"]]

df_merge = df_atletas.merge(df_clubes, how="left", on="atletas.clube_id")

rodada = df_merge.loc[0, "atletas.rodada_id"].astype(str)
year = date.today().year
file = join("data", "01_raw", str(year), f"rodada-{rodada}.csv")

df_merge.to_csv(file, index=False)
# json.dump(data_json, open(file.replace(".csv", ".json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
