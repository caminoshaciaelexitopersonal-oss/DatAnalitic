import pandas as pd
from typing import Dict, Any

def validate_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validates a DataFrame and extracts its schema and basic metadata.

    Args:
        df: The pandas DataFrame to validate.

    Returns:
        A dictionary containing metadata about the schema, including column types,
        null counts, and basic statistics.
    """
    try:
        # Get column data types
        types = {col: str(dtype) for col, dtype in df.dtypes.items()}

        # Get null counts
        null_counts = {col: int(df[col].isnull().sum()) for col in df.columns}

        # Get basic descriptive statistics for numeric columns
        numeric_stats = df.describe(include='number').to_dict()

        # Get summary for object/categorical columns
        categorical_stats = df.describe(include=['object', 'category']).to_dict()

        schema_metadata = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": {
                col: {
                    "dtype": types[col],
                    "null_count": null_counts[col],
                }
                for col in df.columns
            },
            "statistics": {
                "numeric": numeric_stats,
                "categorical": categorical_stats,
            }
        }
        return schema_metadata

    except Exception as e:
        return {"error": f"Failed to validate schema: {str(e)}"}
