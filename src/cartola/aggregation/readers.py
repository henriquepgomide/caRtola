"""Raw-shape readers. Each reader returns a single per-(player, round) DataFrame
with the raw column names — renaming/harmonization happens downstream.

Three shapes correspond to three eras of the project:
- season_files: jogadores.csv + scouts_raw.csv + times.csv (2014–2016)
- monolithic:   single <year>_scouts_raw.csv with player+team metadata (2017)
- round_files:  rodada-N.csv per round, concatenated (2018+)
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

_ROUND_FILE_RE = re.compile(r"rodada-(\d+)\.csv$", re.IGNORECASE)


def read_season_files(raw_dir: str, year: int) -> pd.DataFrame:
    """2014–2016: merge `<year>_scouts_raw.csv` (per-round data) with
    `<year>_jogadores.csv` (player metadata) and `<year>_times.csv` (team names).

    Returns a wide DataFrame keyed by (AtletaID, Rodada) with team `Nome`.
    """
    base = Path(raw_dir)
    scouts = pd.read_csv(base / f"{year}_scouts_raw.csv")
    jogadores = pd.read_csv(base / f"{year}_jogadores.csv")
    times = pd.read_csv(base / f"{year}_times.csv")

    # 2014 scouts has a `Posicao` column that is redundant with jogadores.PosicaoID
    # (both int, same values). Drop to avoid a duplicate column after the merge.
    if "Posicao" in scouts.columns:
        scouts = scouts.drop(columns=["Posicao"])

    jog_keep = jogadores[["ID", "Apelido", "PosicaoID"]].rename(columns={"ID": "AtletaID"})
    df = scouts.merge(jog_keep, on="AtletaID", how="left")

    times_keep = times[["ID", "Nome"]].rename(columns={"ID": "ClubeID"})
    df = df.merge(times_keep, on="ClubeID", how="left")

    return df


def read_monolithic(raw_dir: str, year: int) -> pd.DataFrame:
    """2017: a single CSV containing player metadata + scouts in one wide table."""
    path = Path(raw_dir) / f"{year}_scouts_raw.csv"
    return pd.read_csv(path)


def read_round_files(raw_dir: str, year: int) -> pd.DataFrame:
    """2018+: per-round files `rodada-N.csv`. Concat everything."""
    base = Path(raw_dir)
    if not base.exists():
        logger.warning("Raw dir does not exist: %s", base)
        return pd.DataFrame()

    files = sorted(
        (p for p in base.glob("rodada-*.csv") if _ROUND_FILE_RE.search(p.name)),
        key=lambda p: int(_ROUND_FILE_RE.search(p.name).group(1)),
    )
    if not files:
        logger.warning("No rodada-*.csv files in %s", base)
        return pd.DataFrame()

    frames = [pd.read_csv(p) for p in files]
    return pd.concat(frames, ignore_index=True)
