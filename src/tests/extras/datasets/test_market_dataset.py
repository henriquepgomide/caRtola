import json

import fsspec
import pandas as pd
import pytest
from kedro.io import PartitionedDataSet

from cartola.commons.dataframes import concat_partitioned_datasets
from cartola.extras.datasets.market_dataset import MarketDataSet


@pytest.fixture
def market_data():
    return {
        "atletas": [
            {"atleta_id": 10, "apelido": "João", "scout": {"G": 1}},
            {"atleta_id": 20, "apelido": "Luís", "scout": {"A": 2}},
        ]
    }


@pytest.fixture
def expected_frame():
    return pd.DataFrame(
        {
            "atleta_id": [10, 20],
            "apelido": ["João", "Luís"],
            "G": [1.0, float("nan")],
            "A": [float("nan"), 2.0],
        }
    )


@pytest.mark.parametrize("protocol", ["local", "file", "memory"])
def test_load_market_data(tmp_path, market_data, expected_frame, protocol):
    path = tmp_path / "mercado.txt"
    filepath = {
        "local": str(path),
        "file": path.as_uri(),
        "memory": f"memory:///{tmp_path.name}/mercado.txt",
    }[protocol]
    with fsspec.open(filepath, "w", encoding="latin-1") as file:
        json.dump(market_data, file, ensure_ascii=False)

    pd.testing.assert_frame_equal(MarketDataSet(filepath).load(), expected_frame)


def test_load_partitioned_market_data(tmp_path, market_data, expected_frame):
    path = f"memory:///{tmp_path.name}"
    for round_number in (1, 2):
        with fsspec.open(f"{path}/rodada-{round_number}.txt", "w", encoding="latin-1") as file:
            json.dump(market_data, file, ensure_ascii=False)

    dataset = PartitionedDataSet(path=path, dataset=MarketDataSet, filename_suffix=".txt")
    result = concat_partitioned_datasets(dataset.load())

    pd.testing.assert_frame_equal(result, pd.concat([expected_frame, expected_frame], ignore_index=True))
