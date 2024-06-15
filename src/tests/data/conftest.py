import pandas as pd
import pytest


@pytest.fixture
def data_aggregated():
    return pd.read_csv("data/04_feature/aggregated.csv")
