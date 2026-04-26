import numpy as np
import pandas as pd

from cartola.pipelines.preprocessing.nodes import (
    add_year_column,
    fill_empty_slugs,
    fill_scouts_with_zeros,
    map_posicao_to_string,
    map_status_id_to_string,
)


def test_fill_scouts_with_zeros():
    df = pd.DataFrame(dict(a=[np.nan, 2, np.nan]))
    df = fill_scouts_with_zeros(df, dict(a=1.0))
    assert ~df.a.isna().any()


def test_fill_scouts_with_zeros_no_op_when_no_scout_cols_present():
    """If none of the requested scout columns exist on the frame, return it
    unchanged. The same scouts dict is shared across years that may or may
    not carry the columns; callers depend on this no-op behavior.
    """
    df = pd.DataFrame(dict(other=[1, 2, 3]))
    out = fill_scouts_with_zeros(df, dict(G=0.0, A=0.0))
    assert out is df
    assert list(out.columns) == ["other"]


def test_fill_empty_slugs():
    data = dict(apelido=["Cristiano Ronaldo", "Messi"], slug=["CR7", np.nan])
    df = pd.DataFrame(data)
    df = fill_empty_slugs(df)
    assert "slug" in df.columns
    assert ~df.slug.isna().any()
    assert df.slug.values[-1] == "messi"


def test_fill_empty_slug_with_no_slug_col():
    df = pd.DataFrame(dict(apelido=["Cristiano Ronaldo", "Messi"]))
    df = fill_empty_slugs(df)
    assert "slug" in df.columns
    assert ~df.slug.isna().any()


def test_map_status_id_to_string():
    dict_map = {2: "Dúvida", 3: "Suspenso"}
    df = pd.DataFrame(dict(status=[2, 3]))
    df = map_status_id_to_string(df, dict_map)
    assert df.status.isin(list(dict_map.values())).all()


def test_map_status_id_to_string_with_no_status_col():
    df = pd.DataFrame()
    df_res = map_status_id_to_string(df, {})
    assert df.equals(df_res)


def test_map_posicao_to_string():
    dict_map = {"1": "gol", "2": "lat"}
    df = pd.DataFrame(dict(posicao=[1, 2]))
    df = map_posicao_to_string(df, dict_map)
    assert df.posicao.isin(list(dict_map.values())).all()


def test_add_year_columns():
    df = pd.DataFrame()
    df = add_year_column(df, year=2000)
    assert "ano" in df.columns
    assert np.all(df.ano.values == 2000)
