# backend/tests/test_etl_pipeline.py
import pandas as pd
import pytest
import numpy as np
from unittest.mock import MagicMock

from backend.mpa.etl.service import EtlService

@pytest.fixture
def state_store():
    """Provides a mocked StateStore for tests."""
    return MagicMock()

@pytest.fixture
def etl_service(state_store):
    """Provides an instance of the EtlService."""
    return EtlService(state_store)

def test_standardize_df_handles_mixed_types_and_nulls(etl_service):
    """
    Tests the core cleaning and type conversion logic of the EtlService.
    """
    data = {
        'col_a': ['1', '2', '3', '4', '5'],
        'col_b': [' 10 ', '20', ' 30 ', '40', '50 '],
        'col_c': ['$1,000.00', ' $2,000.00 ', '3,000.00', '4000', '5000.50'],
        'col_d': ['50%', '60 %', ' 70%', '80', '90'],
        'col_e': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', 'not_a_date'],
        'col_f': ['NA', 'N/A', '', '  ', 'valid_string'],
        'col_g': ['(100)', '200', '-300', '400', '500'] # Negative numbers in accounting format
    }
    df = pd.DataFrame(data)

    cleaned_df = etl_service.standardize_df(df)

    # --- Verification ---
    # Integer conversion and stripping whitespace
    assert pd.api.types.is_numeric_dtype(cleaned_df['col_a'])
    assert cleaned_df['col_a'].tolist() == [1, 2, 3, 4, 5]

    # Stripping whitespace
    assert pd.api.types.is_numeric_dtype(cleaned_df['col_b'])
    assert cleaned_df['col_b'].tolist() == [10, 20, 30, 40, 50]

    # Currency and comma cleaning
    assert pd.api.types.is_numeric_dtype(cleaned_df['col_c'])
    assert cleaned_df['col_c'].tolist() == [1000.0, 2000.0, 3000.0, 4000.0, 5000.5]

    # Percentage conversion to float
    assert pd.api.types.is_numeric_dtype(cleaned_df['col_d'])
    assert np.allclose(cleaned_df['col_d'].tolist(), [0.5, 0.6, 0.7, 80.0, 90.0]) # Note: 80 and 90 are not treated as %

    # Datetime conversion (with one failed value remaining as NaT)
    assert pd.api.types.is_datetime64_any_dtype(cleaned_df['col_e'])
    assert pd.isna(cleaned_df['col_e'].iloc[4]) # 'not_a_date' should become NaT

    # Null value standardization
    assert cleaned_df['col_f'].isna().sum() == 4
    assert cleaned_df['col_f'].iloc[4] == 'valid_string'

    # Accounting negative format
    assert pd.api.types.is_numeric_dtype(cleaned_df['col_g'])
    assert cleaned_df['col_g'].tolist() == [-100, 200, -300, 400, 500]


def test_heuristic_conversion_thresholds(etl_service):
    """
    Tests the 80% rule for type conversion.
    """
    # This column is >80% numeric, should be converted
    data_numeric_pass = {'col': ['1', '2', '3', '4', 'fail']}
    df_numeric_pass = pd.DataFrame(data_numeric_pass)
    cleaned_df_np = etl_service.standardize_df(df_numeric_pass)
    assert pd.api.types.is_numeric_dtype(cleaned_df_np['col'])

    # This column is <80% numeric, should remain as object
    data_numeric_fail = {'col': ['1', '2', '3', 'fail1', 'fail2']}
    df_numeric_fail = pd.DataFrame(data_numeric_fail)
    cleaned_df_nf = etl_service.standardize_df(df_numeric_fail)
    assert pd.api.types.is_object_dtype(cleaned_df_nf['col'])

    # This column is >80% datetime, should be converted
    data_date_pass = {'col': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', 'fail']}
    df_date_pass = pd.DataFrame(data_date_pass)
    cleaned_df_dp = etl_service.standardize_df(df_date_pass)
    assert pd.api.types.is_datetime64_any_dtype(cleaned_df_dp['col'])
