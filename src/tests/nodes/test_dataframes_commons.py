import pandas as pd

from cartola.commons.dataframes import (
    concat_partitioned_datasets,
    drop_columns,
)


def test_concat_partitioned_datasets_concatenates_all_partitions():
    parts = {
        "preprocessed_2018": lambda: pd.DataFrame({"a": [1, 2], "b": ["x", "y"]}),
        "preprocessed_2014": lambda: pd.DataFrame({"a": [3], "b": ["z"]}),
        "preprocessed_2020": lambda: pd.DataFrame({"a": [4, 5, 6], "b": ["p", "q", "r"]}),
    }
    out = concat_partitioned_datasets(parts)
    assert len(out) == 6
    assert sorted(out["a"].tolist()) == [1, 2, 3, 4, 5, 6]
    assert set(out["b"]) == {"x", "y", "z", "p", "q", "r"}


def test_concat_partitioned_datasets_handles_empty_input():
    out = concat_partitioned_datasets({})
    assert isinstance(out, pd.DataFrame)
    assert len(out) == 0


def test_concat_partitioned_datasets_resets_index():
    parts = {
        "p1": lambda: pd.DataFrame({"a": [1, 2]}, index=[10, 11]),
        "p2": lambda: pd.DataFrame({"a": [3]}, index=[99]),
    }
    out = concat_partitioned_datasets(parts)
    assert list(out.index) == [0, 1, 2]


def test_drop_columns_drops_listed_columns():
    df = pd.DataFrame({"a": [1], "b": [2], "c": [3]})
    out = drop_columns(df, ["b"])
    assert list(out.columns) == ["a", "c"]


def test_drop_columns_tolerates_missing_columns():
    """drop_columns must not raise when a requested column is absent.

    The per-year drop_columns parameter is shared across years with
    slightly different schemas; demanding strict membership would
    require a separate parameter file per year just to omit one column.
    """
    df = pd.DataFrame({"a": [1], "b": [2]})
    out = drop_columns(df, ["b", "does_not_exist", "also_missing"])
    assert list(out.columns) == ["a"]


def test_drop_columns_with_empty_list_returns_same_columns():
    df = pd.DataFrame({"a": [1], "b": [2]})
    out = drop_columns(df, [])
    assert list(out.columns) == ["a", "b"]
