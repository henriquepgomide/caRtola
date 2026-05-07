"""Raw-shape readers for the four eras of Cartola data.

Each reader returns a single per-(player, round) DataFrame with the raw column
names — renaming/harmonization happens downstream.

The four shapes correspond to four eras of the project:

* ``season_files``: ``jogadores.csv`` + ``scouts_raw.csv`` + ``times.csv`` (2014-2016).
* ``monolithic``:   single ``<year>_scouts_raw.csv`` with player+team metadata (2017).
* ``round_files``:  ``rodada-N.csv`` per round, concatenated (2018-2020, 2022+).
* ``mercado_json``: JSON ``Mercado_N.txt`` snapshots, latin-1 encoded (2021 only).
"""

import io
import json
import logging
import re
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

_ROUND_FILE_RE = re.compile(r"rodada-(\d+)\.csv$", re.IGNORECASE)
_MERCADO_FILE_RE = re.compile(r"Mercado_(\d+)\.txt$", re.IGNORECASE)


_MOJIBAKE_SIGNATURE = b"\xc3\x83\xc2"
"""Strong double-encoding signature.

A ``Ã`` (``\\xc3\\x83``) immediately followed by a ``Â`` (``\\xc3\\x82``) start
byte — that 4-byte sequence is what you get when a UTF-8 file is decoded as
latin-1 and re-encoded as UTF-8. A naive marker like just ``\\xc3\\x83`` triggers
false positives on legitimate accented words such as ``São`` or ``ração``.
"""


def _read_csv_robust(path: Path) -> pd.DataFrame:
    """Read a Cartola CSV, repairing common encoding pitfalls.

    Two real-world cases are handled:

    1. Genuine latin-1 file (rare in this corpus) → ``UnicodeDecodeError``
       on UTF-8 read; retry as latin-1.
    2. Double-encoded UTF-8 (notably 2023's ``rodada-N.csv``) → reads as
       valid UTF-8 but contains mojibake like ``SÃ£o Paulo`` instead of
       ``São Paulo``. Detected via the ``Ã Â`` 3-byte signature in the file
       (sampling several KB to handle long single-line headers). Repaired
       by ``decode utf-8 → encode latin-1 → decode utf-8``.

    Args:
        path: Path to the CSV file.

    Returns:
        Parsed DataFrame.
    """
    try:
        sample = path.open("rb").read(65536)
    except OSError:
        return pd.read_csv(path)

    if _MOJIBAKE_SIGNATURE in sample:
        try:
            text = path.read_bytes().decode("utf-8").encode("latin-1").decode("utf-8")
            return pd.read_csv(io.StringIO(text))
        except (UnicodeDecodeError, UnicodeEncodeError):
            logger.warning("Mojibake repair failed for %s; reading as-is", path)

    try:
        return pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        logger.warning("UTF-8 decode failed for %s — falling back to latin-1", path)
        return pd.read_csv(path, encoding="latin-1")


def read_season_files(raw_dir: str, year: int) -> pd.DataFrame:
    """Read the 2014-2016 three-file shape.

    Merges ``<year>_scouts_raw.csv`` (per-round data) with
    ``<year>_jogadores.csv`` (player metadata) and ``<year>_times.csv``
    (team names).

    Args:
        raw_dir: Directory containing the three CSVs for ``year``.
        year: Season year (2014-2016).

    Returns:
        Wide DataFrame keyed by ``(AtletaID, Rodada)`` with team ``Nome``.
    """
    base = Path(raw_dir)
    scouts = _read_csv_robust(base / f"{year}_scouts_raw.csv")
    jogadores = _read_csv_robust(base / f"{year}_jogadores.csv")
    times = _read_csv_robust(base / f"{year}_times.csv")

    if "Posicao" in scouts.columns:
        scouts = scouts.drop(columns=["Posicao"])

    jog_keep = jogadores[["ID", "Apelido", "PosicaoID"]].rename(columns={"ID": "AtletaID"})
    df = scouts.merge(jog_keep, on="AtletaID", how="left")

    times_keep = times[["ID", "Nome"]].rename(columns={"ID": "ClubeID"})
    df = df.merge(times_keep, on="ClubeID", how="left")

    return df


def read_monolithic(raw_dir: str, year: int) -> pd.DataFrame:
    """Read the 2017 single-file shape.

    Args:
        raw_dir: Directory containing ``<year>_scouts_raw.csv``.
        year: Season year (2017).

    Returns:
        Wide DataFrame containing player metadata + scouts in one table.
    """
    path = Path(raw_dir) / f"{year}_scouts_raw.csv"
    return _read_csv_robust(path)


def read_round_files(raw_dir: str, year: int) -> pd.DataFrame:
    """Read the 2018+ per-round file shape (``rodada-N.csv``) and concat.

    The file name is treated as the source of truth for which round each
    snapshot represents — the upstream ``atletas.rodada_id`` field is
    overwritten because it is occasionally stale (e.g. 2023 ships both
    ``rodada-1.csv`` and ``rodada-2.csv`` carrying internal ``rodada_id=2``,
    and 2022 ships a preseason ``rodada-0.csv`` that internally claims
    ``rodada_id=1`` and would otherwise duplicate the actual round 1).
    ``rodada-0.csv`` (preseason) is dropped entirely.

    Args:
        raw_dir: Directory containing ``rodada-*.csv`` files.
        year: Season year (unused; ``raw_dir`` already encodes it).

    Returns:
        Concatenated DataFrame across all valid rounds. An empty DataFrame
        is returned when ``raw_dir`` does not exist or has no matching files.
    """
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

    frames: list[pd.DataFrame] = []
    for path in files:
        rodada = int(_ROUND_FILE_RE.search(path.name).group(1))
        if rodada < 1:
            logger.info("Skipping preseason snapshot %s", path.name)
            continue
        frame = _read_csv_robust(path)
        frame["atletas.rodada_id"] = rodada
        frames.append(frame)

    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


_MERCADO_ATLETA_FIELDS: tuple[str, ...] = (
    "atleta_id",
    "clube_id",
    "posicao_id",
    "status_id",
    "pontos_num",
    "preco_num",
    "variacao_num",
    "media_num",
    "jogos_num",
    "slug",
    "apelido",
    "apelido_abreviado",
    "nome",
    "foto",
)
"""Atleta-level fields lifted from each Mercado JSON entry.

Names match the ``clube_id`` / ``atleta_id`` form already covered by
:data:`~cartola.aggregation.columns.COLUMN_RENAME_MAP`, so the downstream
rename step works without special-casing 2021.
"""


def read_mercado_json(raw_dir: str, year: int) -> pd.DataFrame:
    """Read the 2021 per-round JSON ``Mercado_N.txt`` shape.

    Each ``Mercado_N.txt`` is the Cartola market state at the start of round
    ``N``, which means it carries cumulative stats from rounds ``1..N-1`` —
    except for ``Mercado_1.txt``, which is the preseason snapshot with empty
    scouts and is therefore skipped (it would otherwise duplicate the
    ``rodada=1`` row that comes from ``Mercado_2.txt``).

    Each player row is labelled with ``rodada_id = N - 1`` and the nested
    ``scout: {SCOUT: count, ...}`` dict is flattened to top-level columns so
    the same downstream pipeline as :func:`read_round_files` applies.

    Args:
        raw_dir: Directory containing ``Mercado_*.txt`` files.
        year: Season year (unused; ``raw_dir`` already encodes it).

    Returns:
        DataFrame across all post-preseason rounds. Returns an empty
        DataFrame when ``raw_dir`` is missing or has no matching files.
    """
    base = Path(raw_dir)
    if not base.exists():
        logger.warning("Raw dir does not exist: %s", base)
        return pd.DataFrame()

    files = sorted(
        (p for p in base.glob("Mercado_*.txt") if _MERCADO_FILE_RE.search(p.name)),
        key=lambda p: int(_MERCADO_FILE_RE.search(p.name).group(1)),
    )
    if not files:
        logger.warning("No Mercado_*.txt files in %s", base)
        return pd.DataFrame()

    rows: list[dict[str, object]] = []
    for path in files:
        idx = int(_MERCADO_FILE_RE.search(path.name).group(1))
        if idx < 2:
            continue

        try:
            with path.open(encoding="utf-8") as fh:
                payload = json.load(fh)
        except UnicodeDecodeError:
            with path.open(encoding="latin-1") as fh:
                payload = json.load(fh)

        clubes = payload.get("clubes") or {}
        for atleta in payload.get("atletas") or []:
            row: dict[str, object] = {f: atleta.get(f) for f in _MERCADO_ATLETA_FIELDS}
            row["rodada_id"] = idx - 1
            clube_id = atleta.get("clube_id")
            row["atletas.clube.id.full.name"] = (clubes.get(str(clube_id)) or {}).get("nome")
            row.update(atleta.get("scout") or {})
            rows.append(row)

    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)
