import pandas as pd
import pytest
from backend.mpa.ingestion.schema_validator import validate_dataframe

@pytest.fixture
def sample_dataframe():
    """Provides a sample DataFrame for testing."""
    data = {
        'numeric_col': [1, 2, 3, 4, 5.5, None],
        'categorical_col': ['A', 'B', 'A', 'C', 'B', 'A'],
        'date_col': pd.to_datetime(['2021-01-01', '2021-01-02', '2021-01-03', '2021-01-04', '2021-01-05', '2021-01-06'])
    }
    return pd.DataFrame(data)

def test_validate_dataframe_structure(sample_dataframe):
    """Tests that the basic structure of the metadata is correct."""
    metadata = validate_dataframe(sample_dataframe)

    assert "error" not in metadata
    assert "row_count" in metadata
    assert "column_count" in metadata
    assert "columns" in metadata
    assert "statistics" in metadata
    assert metadata["row_count"] == 6
    assert metadata["column_count"] == 3

def test_validate_dataframe_column_types(sample_dataframe):
    """Tests that column data types and nulls are correctly identified."""
    metadata = validate_dataframe(sample_dataframe)

    columns_meta = metadata["columns"]
    assert columns_meta['numeric_col']['dtype'] == 'float64'
    assert columns_meta['numeric_col']['null_count'] == 1
    assert columns_meta['categorical_col']['dtype'] == 'object'
    assert columns_meta['categorical_col']['null_count'] == 0
    assert 'datetime' in columns_meta['date_col']['dtype']

def test_validate_dataframe_statistics(sample_dataframe):
    """Tests that statistics are generated for numeric and categorical columns."""
    metadata = validate_dataframe(sample_dataframe)

    stats = metadata["statistics"]
    assert "numeric" in stats
    assert "categorical" in stats
    assert "numeric_col" in stats["numeric"]
    assert "categorical_col" in stats["categorical"]
    assert "count" in stats["numeric"]["numeric_col"]
    assert stats["numeric"]["numeric_col"]["count"] == 5
    assert "unique" in stats["categorical"]["categorical_col"]
    assert stats["categorical"]["categorical_col"]["unique"] == 3
