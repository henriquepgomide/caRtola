import pandas as pd

from cartola.commons.dataframes import (
    concat_partitioned_datasets,
    drop_columns,
    drop_duplicated_rows,
    rename_cols,
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


def test_drop_duplicated_rows_removes_exact_duplicates_and_resets_index():
    df = pd.DataFrame({"a": [1, 1, 2, 2], "b": ["x", "x", "y", "y"]}, index=[10, 11, 12, 13])
    out = drop_duplicated_rows(df)
    assert len(out) == 2
    assert list(out.index) == [0, 1]
    assert out["a"].tolist() == [1, 2]


def test_drop_duplicated_rows_keeps_distinct_rows_unchanged():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    out = drop_duplicated_rows(df)
    assert len(out) == 3
    assert out["a"].tolist() == [1, 2, 3]


def test_drop_duplicated_rows_treats_partial_overlap_as_distinct():
    """Rows that share some but not all column values are not duplicates."""
    df = pd.DataFrame({"a": [1, 1], "b": ["x", "y"]})
    out = drop_duplicated_rows(df)
    assert len(out) == 2


def test_rename_cols_renames_using_mapping():
    df = pd.DataFrame({"a": [1], "b": [2]})
    out = rename_cols(df, {"a": "alpha", "b": "beta"})
    assert list(out.columns) == ["alpha", "beta"]
    assert out["alpha"].iloc[0] == 1


def test_rename_cols_ignores_keys_not_in_columns():
    """Mapping keys that don't match any column are silently ignored."""
    df = pd.DataFrame({"a": [1]})
    out = rename_cols(df, {"a": "alpha", "missing": "x"})
    assert list(out.columns) == ["alpha"]


def test_rename_cols_with_empty_mapping_returns_same_columns():
    df = pd.DataFrame({"a": [1], "b": [2]})
    out = rename_cols(df, {})
    assert list(out.columns) == ["a", "b"]
