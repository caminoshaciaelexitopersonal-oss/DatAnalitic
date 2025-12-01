import pandas as pd
import hashlib
from typing import List

class ComplianceService:
    """
    MPA service for compliance tasks, such as PII anonymization.
    """
    # Simple keyword-based detection for potential PII columns
    PII_KEYWORDS = ['email', 'phone', 'ssn', 'address', 'nombre', 'id', 'user']

    def _hash_value(self, value: str) -> str:
        """Hashes a single string value using SHA-256."""
        if value is None:
            return None
        return hashlib.sha256(str(value).encode()).hexdigest()

    def find_pii_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Finds columns that potentially contain Personally Identifiable Information (PII)
        based on keyword matching in column names.
        """
        pii_columns = []
        for col in df.columns:
            if any(keyword in col.lower() for keyword in self.PII_KEYWORDS):
                pii_columns.append(col)
        return pii_columns

    def anonymize_dataframe(self, df: pd.DataFrame, columns_to_anonymize: List[str] = None) -> pd.DataFrame:
        """
        Anonymizes specified columns in a DataFrame by hashing their values.
        If no columns are specified, it attempts to auto-detect them.
        """
        anonymized_df = df.copy()

        if columns_to_anonymize is None:
            columns_to_anonymize = self.find_pii_columns(anonymized_df)

        for col in columns_to_anonymize:
            if col in anonymized_df.columns:
                anonymized_df[col] = anonymized_df[col].apply(self._hash_value)

        return anonymized_df

# --- Dependency Injection ---
compliance_service = ComplianceService()

def get_compliance_service() -> ComplianceService:
    return compliance_service
