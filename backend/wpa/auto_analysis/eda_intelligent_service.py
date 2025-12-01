import pandas as pd
from typing import Dict, Any, List
from scipy import stats
import os
import json
import matplotlib.pyplot as plt
import seaborn as sns

class EDAIntelligentService:
    """
    Performs automated Exploratory Data Analysis (EDA) on a given dataset,
    returning reports and visualizations as artifacts.
    """

    def __init__(self, dataframe: pd.DataFrame, inferred_types: Dict[str, str]):
        self.df = dataframe
        self.inferred_types = inferred_types
        self.classified_types = self._classify_variables()

    def _classify_variables(self) -> Dict[str, str]:
        """Refines the initial type inference into more specific statistical types."""
        classified = {}
        for col, base_type in self.inferred_types.items():
            if base_type == 'numeric':
                unique_count = self.df[col].nunique()
                if unique_count == 2:
                    classified[col] = 'binary'
                elif unique_count < 20:
                    classified[col] = 'numeric_discrete'
                else:
                    classified[col] = 'numeric_continuous'
            else:
                classified[col] = base_type
        return classified

    def run_automated_eda(self) -> Dict[str, Any]:
        """Orchestrates the generation of all EDA artifacts and returns them."""
        summary_stats = self.auto_summary()
        missing_report, missing_heatmap = self.missing_report()
        distribution_plots = self._generate_distribution_visuals()

        full_report = {
            "variable_classification": self.classified_types,
            "outlier_report": self._detect_outliers(),
            "correlation_matrix": self._get_correlation_matrix(),
            "normality_tests": self._run_normality_tests(),
        }

        return {
            "json_artifacts": {
                "summary_statistics.json": summary_stats,
                "missing_values_report.json": missing_report,
                "eda_full_report.json": full_report,
            },
            "figure_artifacts": {
                "missing_values_heatmap.png": missing_heatmap,
                **distribution_plots,
            }
        }

    def auto_summary(self) -> Dict[str, Any]:
        """Generates a summary of descriptive statistics."""
        stats = {}
        for col, var_type in self.classified_types.items():
            if var_type.startswith('numeric') or var_type == 'binary':
                stats[col] = self.df[col].describe().to_dict()
            elif var_type.startswith('categorical'):
                stats[col] = self.df[col].describe().to_dict()
        return stats

    def missing_report(self) -> (Dict[str, Any], plt.Figure):
        """Generates a JSON report and a heatmap for missing values."""
        missing_count = self.df.isnull().sum()
        missing_percent = (missing_count / len(self.df)) * 100
        report = {col: {"count": int(missing_count[col]), "percentage": missing_percent[col]} for col in self.df.columns}

        fig = None
        try:
            fig = plt.figure(figsize=(12, 8))
            sns.heatmap(self.df.isnull(), cbar=False, cmap='viridis')
            plt.title('Missing Values Heatmap')
            plt.tight_layout()
        except Exception as e:
            print(f"Could not generate missing values heatmap. Error: {e}")
            plt.close('all')

        return report, fig

    def _detect_outliers(self, iqr_multiplier: float = 1.5) -> Dict[str, List[Any]]:
        """Detects outliers in numeric columns using the IQR method."""
        outliers = {}
        for col, var_type in self.classified_types.items():
            if var_type.startswith('numeric'):
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - iqr_multiplier * IQR
                upper_bound = Q3 + iqr_multiplier * IQR
                col_outliers = self.df[(self.df[col] < lower_bound) | (self.df[col] > upper_bound)][col].tolist()
                if col_outliers:
                    outliers[col] = col_outliers
        return outliers

    def _generate_distribution_visuals(self) -> Dict[str, plt.Figure]:
        """Generates distribution plots and returns them as a dictionary of figures."""
        figures = {}
        for col, var_type in self.classified_types.items():
            fig = None
            try:
                fig = plt.figure(figsize=(10, 6))
                if var_type.startswith('numeric'):
                    self.df[col].hist(bins=30)
                    plt.title(f"Histogram of {col}")
                    plt.xlabel(col)
                    plt.ylabel("Frequency")
                elif var_type.startswith('categorical') and self.df[col].nunique() < 50:
                    self.df[col].value_counts().plot(kind='bar')
                    plt.title(f"Bar Chart of {col}")
                    plt.xlabel(col)
                    plt.ylabel("Count")

                plt.tight_layout()
                figures[f"{col}_distribution.png"] = fig
            except Exception as e:
                print(f"Could not generate plot for column '{col}'. Error: {e}")
                if fig:
                    plt.close(fig)
        return figures

    def _get_correlation_matrix(self) -> Dict[str, Any]:
        """Calculates Pearson and Spearman correlation matrices for numeric columns."""
        numeric_cols = [col for col, type in self.classified_types.items() if type.startswith('numeric')]
        if not numeric_cols:
            return {}

        pearson_corr = self.df[numeric_cols].corr(method='pearson').to_dict()
        spearman_corr = self.df[numeric_cols].corr(method='spearman').to_dict()

        return {
            'pearson': pearson_corr,
            'spearman': spearman_corr
        }

    def _run_normality_tests(self, p_value_threshold: float = 0.05) -> Dict[str, Any]:
        """Runs Shapiro-Wilk and Kolmogorov-Smirnov tests for normality on numeric columns."""
        numeric_cols = [col for col, type in self.classified_types.items() if type.startswith('numeric_continuous')]
        results = {}

        for col in numeric_cols:
            # Shapiro-Wilk test (for samples < 5000)
            if len(self.df[col].dropna()) > 2 and len(self.df[col].dropna()) < 5000:
                shapiro_stat, shapiro_p = stats.shapiro(self.df[col].dropna())
                shapiro_is_normal = shapiro_p > p_value_threshold
            else:
                shapiro_stat, shapiro_p, shapiro_is_normal = None, None, None

            # Kolmogorov-Smirnov test
            ks_stat, ks_p = stats.kstest(self.df[col].dropna(), 'norm')
            ks_is_normal = ks_p > p_value_threshold

            results[col] = {
                'shapiro': {'statistic': shapiro_stat, 'p_value': shapiro_p, 'is_normal': shapiro_is_normal},
                'kolmogorov_smirnov': {'statistic': ks_stat, 'p_value': ks_p, 'is_normal': ks_is_normal},
            }
        return results

def run_eda(df: pd.DataFrame, inferred_types: Dict[str, str], job_id: str):
    """
    Entrypoint function to run the full automated EDA process.
    """
    service = EDAIntelligentService(df, inferred_types, job_id)
    service.run_automated_eda()
