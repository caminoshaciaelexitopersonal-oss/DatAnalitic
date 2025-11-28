import pandas as pd
from scipy import stats
from typing import Dict, Any, List

class StatsEngine:
    """
    Performs automated statistical testing based on variable types.
    """
    def __init__(self, df: pd.DataFrame, classified_types: Dict[str, str]):
        self.df = df
        self.classified_types = classified_types

    def _run_chi_squared(self, var1: str, var2: str) -> Dict[str, Any]:
        """Runs Chi-squared test for two categorical variables."""
        contingency_table = pd.crosstab(self.df[var1], self.df[var2])
        chi2, p, _, _ = stats.chi2_contingency(contingency_table)
        return {
            "test": "Chi-squared",
            "variables": [var1, var2],
            "statistic": chi2,
            "p_value": p,
            "comment": "Evaluates independence between two categorical variables."
        }

    def _run_anova(self, categorical_var: str, numerical_var: str) -> Dict[str, Any]:
        """Runs ANOVA test for a categorical and a numerical variable."""
        groups = [group[numerical_var].dropna() for name, group in self.df.groupby(categorical_var)]
        f_stat, p_val = stats.f_oneway(*groups)
        return {
            "test": "ANOVA",
            "variables": [categorical_var, numerical_var],
            "statistic": f_stat,
            "p_value": p_val,
            "comment": "Compares means of a numerical variable across multiple categories."
        }

    def _run_pearson(self, var1: str, var2: str) -> Dict[str, Any]:
        """Runs Pearson correlation for two numerical variables."""
        corr, p_val = stats.pearsonr(self.df[var1].dropna(), self.df[var2].dropna())
        return {
            "test": "Pearson Correlation",
            "variables": [var1, var2],
            "statistic": corr,
            "p_value": p_val,
            "comment": "Measures linear relationship between two numerical variables."
        }

    def run_tests_against_target(self, target: str) -> List[Dict[str, Any]]:
        """
        Automatically selects and runs the appropriate statistical test for each
        feature against the target variable.
        """
        results = []
        target_type = self.classified_types.get(target)
        if not target_type:
            return []

        for feature, feature_type in self.classified_types.items():
            if feature == target:
                continue

            # Case 1: Categorical vs Categorical
            if feature_type == 'categorical' and target_type == 'categorical':
                results.append(self._run_chi_squared(feature, target))

            # Case 2: Numerical vs Categorical
            elif feature_type.startswith('numeric') and target_type == 'categorical':
                results.append(self._run_anova(target, feature))
            elif feature_type == 'categorical' and target_type.startswith('numeric'):
                 results.append(self._run_anova(feature, target))

            # Case 3: Numerical vs Numerical
            elif feature_type.startswith('numeric') and target_type.startswith('numeric'):
                results.append(self._run_pearson(feature, target))

        return results
