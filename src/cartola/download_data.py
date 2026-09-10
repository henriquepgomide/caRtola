"""Download the current Cartola FC market snapshot and persist it as raw CSV."""

import logging
import os
from datetime import date
from os.path import exists, join

import pandas as pd
import requests


HTTP_TIMEOUT_SECONDS = 30
MARKET_URL = "https://api.cartolafc.globo.com/atletas/mercado"

logger = logging.getLogger(__name__)


def main() -> None:
    """Fetch the current round market data and write it to data/01_raw/<year>/."""
    data_json = requests.get(MARKET_URL, timeout=HTTP_TIMEOUT_SECONDS).json()

    df_atletas = pd.DataFrame(data_json["atletas"])
    df_atletas = df_atletas.join(pd.DataFrame(df_atletas.pop("scout").values.tolist()))
    df_atletas = df_atletas.rename(
        columns={col: f"atletas.{col}" if col.islower() else col for col in df_atletas.columns}
    )

    df_clubes = pd.DataFrame(data_json["clubes"].values())
    df_clubes = df_clubes.rename(
        columns=dict(id="atletas.clube_id", nome="atletas.clube.id.full.name")
    )
    df_clubes = df_clubes[["atletas.clube_id", "atletas.clube.id.full.name"]]

    df_merge = df_atletas.merge(df_clubes, how="left", on="atletas.clube_id")

    rodada = df_merge.loc[0, "atletas.rodada_id"].astype(str)
    year = date.today().year
    file = join("data", "01_raw", str(year), f"rodada-{rodada}.csv")
    logger.info("Writing market snapshot to %s", file)

    cols_scouts = sorted([col for col in df_merge.columns if col.isupper()])
    cols_atleta = sorted(set(df_merge.columns) - set(cols_scouts))

    df_merge = df_merge.loc[:, cols_atleta + cols_scouts]
    df_merge.sort_values(by="atletas.atleta_id", inplace=True, ignore_index=True)

    if not exists(file):
        os.makedirs(os.path.dirname(file), exist_ok=True)
        df_merge.to_csv(file, index=False)


if __name__ == "__main__":
    main()
