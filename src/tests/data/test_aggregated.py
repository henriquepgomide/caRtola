from cartola.schemas.aggregated import AggregatedSchema


def test_aggregated_schema(data_aggregated):
    AggregatedSchema.validate(data_aggregated, inplace=True, lazy=True)
