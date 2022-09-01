import json
from pathlib import PurePosixPath
from typing import Any, Dict

import fsspec
import pandas as pd
from kedro.io import AbstractDataSet
from kedro.io.core import get_filepath_str, get_protocol_and_path


class MarketDataSet(AbstractDataSet):
    """A custom dataset to load marked data of 2021 (data/01_raw/2021) as pandas DataFrames."""

    def __init__(self, filepath: str):
        """
        Args:
            filepath: The location of the file to load / save data.
        """
        protocol, path = get_protocol_and_path(filepath)
        self._protocol = protocol
        self._filepath = PurePosixPath(path)
        self._fs = fsspec.filesystem(self._protocol)

    def _load(self) -> pd.DataFrame:
        """Loads data from the json file.

        Returns:
            Data from the json file as a pandas DataFrame.
        """
        load_path = get_filepath_str(self._filepath, self._protocol)
        dict_json = json.load(open(load_path, "r", encoding="latin-1"))
        df = pd.DataFrame(dict_json["atletas"])
        return df.join(pd.DataFrame(df.pop("scout").values.tolist()))

    def _save(self, data: pd.DataFrame) -> None:
        """Saves data to the specified filepath"""
        save_path = get_filepath_str(self._filepath, self._protocol)
        data.to_csv(save_path, index=False)

    def _describe(self) -> Dict[str, Any]:
        """Returns a dict that describes the attributes of the dataset."""
        return dict(filepath=self._filepath, protocol=self._protocol)
