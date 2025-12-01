"""
automl_recommender.py

Lightweight AutoML recommendation engine.
- Input: pandas.DataFrame (df)
- Output: dict of recommendations: charts, KPIs, candidate targets, recommended models.

Usage example:
  from automl_recommender import AutoMLRecommender
  rec = AutoMLRecommender()
  out = rec.recommend(df, max_samples=3000)
"""

import math
import time
import logging
from typing import List, Dict, Any, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_score, StratifiedKFold, KFold, train_test_split
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_selection import mutual_info_classif, mutual_info_regression
from scipy import stats

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# -------------------
# Helpers
# -------------------
def is_numeric_series(s: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(s)


def is_categorical_series(s: pd.Series) -> bool:
    return pd.api.types.is_categorical_dtype(s) or pd.api.types.is_object_dtype(s)


def cardinality(s: pd.Series) -> int:
    return int(s.nunique(dropna=True))


def pct_missing(s: pd.Series) -> float:
    return float(s.isna().mean())


def skewness(s: pd.Series) -> float:
    try:
        return float(stats.skew(s.dropna()))
    except Exception:
        return 0.0


def corr_with_numeric(df: pd.DataFrame, col: str, top_k: int = 10) -> List[Tuple[str, float]]:
    res = []
    if not pd.api.types.is_numeric_dtype(df[col]):
        return res
    for c in df.select_dtypes(include=[np.number]).columns:
        if c == col:
            continue
        try:
            corr = df[col].corr(df[c])
            if not np.isnan(corr):
                res.append((c, abs(float(corr))))
        except Exception:
            continue
    res.sort(key=lambda x: x[1], reverse=True)
    return res[:top_k]


def mutual_info_with_others(df: pd.DataFrame, col: str, top_k: int = 10) -> List[Tuple[str, float]]:
    try:
        X = df.drop(columns=[col])
        # keep numeric features for speed; encode categoricals to numeric counts
        X_num = X.select_dtypes(include=[np.number])
        if X_num.shape[1] == 0:
            return []
        y = pd.factorize(df[col].astype(str))[0]
        mi = mutual_info_classif(X_num.fillna(0), y, discrete_features='auto')
        pairs = list(zip(X_num.columns.tolist(), mi.tolist()))
        pairs.sort(key=lambda x: x[1], reverse=True)
        return pairs[:top_k]
    except Exception:
        return []


def quick_predictability(df: pd.DataFrame, target_col: str, max_samples: int = 2000) -> Dict[str, Any]:
    """
    Cheap predictability estimate:
      - sample up to max_samples
      - select numeric predictors up to 10
      - run DecisionTree (for classification) or Ridge (for regression) with cv=3
    Returns: {'task':'classification'|'regression'|'na','metric':float,'raw_metric':float}
    """
    n = len(df)
    if n < 50:
        return {"task": "na", "metric": 0.0, "note": "insufficient_rows"}

    y = df[target_col]
    task = "regression" if is_numeric_series(y) and cardinality(y) > 15 else "classification" if is_categorical_series(y) or (is_numeric_series(y) and cardinality(y) <= 15) else "na"
    sample_n = min(n, max_samples)
    sample = df.sample(n=sample_n, random_state=42)
    X = sample.drop(columns=[target_col])
    # select numeric predictors
    X_num = X.select_dtypes(include=[np.number]).fillna(0)
    if X_num.shape[1] == 0:
        return {"task": task, "metric": 0.0, "note": "no_numeric_predictors"}

    X_sub = X_num.iloc[:, :min(10, X_num.shape[1])]
    if task == "classification":
        y_enc = pd.factorize(sample[target_col])[0]
        model = DecisionTreeClassifier(max_depth=4, random_state=42)
        cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
        try:
            scores = cross_val_score(model, X_sub, y_enc, cv=cv, scoring="balanced_accuracy", error_score="raise")
            return {"task": "classification", "metric": float(np.mean(scores)), "raw": scores.tolist()}
        except Exception as e:
            logger.exception("Quick predict classification failed: %s", e)
            return {"task": "classification", "metric": 0.0, "error": str(e)}
    elif task == "regression":
        y_reg = sample[target_col].fillna(0)
        model = Ridge()
        cv = KFold(n_splits=3, shuffle=True, random_state=42)
        try:
            scores = cross_val_score(model, X_sub, y_reg, cv=cv, scoring="r2", error_score="raise")
            return {"task": "regression", "metric": float(np.mean(scores)), "raw": scores.tolist()}
        except Exception as e:
            logger.exception("Quick predict regression failed: %s", e)
            return {"task": "regression", "metric": 0.0, "error": str(e)}
    else:
        return {"task": "na", "metric": 0.0}

# -------------------------
# Recommendation Engine
# -------------------------
class AutoMLRecommender:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def recommend(self, df: pd.DataFrame, max_samples: int = 3000) -> Dict[str, Any]:
        """
        Produces a recommendation dict:
         - charts: per column or pair recommended chart type(s)
         - kpis: suggested KPI computations
         - candidate_targets: list of best columns to be used as target (with predictability)
         - recommended_models: top model families with rationale
        """
        start = time.time()
        nrows, ncols = df.shape
        res = {
            "nrows": nrows,
            "ncols": ncols,
            "charts": {},
            "kpis": [],
            "candidate_targets": [],
            "recommended_models": [],
            "notes": []
        }

        # basic column profiling
        profile = {}
        for col in df.columns:
            s = df[col]
            profile[col] = {
                "dtype": str(s.dtype),
                "n_unique": int(s.nunique(dropna=True)),
                "pct_missing": float(s.isna().mean()),
                "skew": skewness(s) if is_numeric_series(s) else None,
                "cardinality": cardinality(s)
            }

        # Suggest charts per column
        for col, info in profile.items():
            if info["pct_missing"] > 0.8:
                res["charts"][col] = ["missing_values_table"]
                continue
            if is_numeric_series(df[col]):
                # if many unique values -> histogram or density
                if info["n_unique"] > 50:
                    res["charts"][col] = ["histogram", "boxplot", "time_series_if_date"]
                else:
                    res["charts"][col] = ["histogram", "boxplot"]
            elif is_categorical_series(df[col]):
                if info["n_unique"] <= 10:
                    res["charts"][col] = ["bar", "pie"]
                else:
                    res["charts"][col] = ["bar_topk", "treemap"]
            else:
                res["charts"][col] = ["table_preview"]

        # Suggest pairwise charts for important numeric pairs (corr)
        # compute numeric correlation matrix
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(num_cols) >= 2:
            corr = df[num_cols].corr().abs().fillna(0)
            # pick top correlated pairs
            pairs = []
            for i, a in enumerate(num_cols):
                for b in num_cols[i+1:]:
                    val = corr.loc[a, b]
                    pairs.append((a, b, float(val)))
            pairs.sort(key=lambda x: x[2], reverse=True)
            top_pairs = [p for p in pairs if p[2] >= 0.4][:6]
            res["notes"].append(f"Top correlated pairs: {top_pairs}")
            for a,b,v in top_pairs:
                res["charts"][f"{a}__{b}"] = ["scatter", "regression_line"]

        # Suggest KPIs
        # heuristics: sums for 'amount','sales','revenue', averages for 'price','cost'
        cols_lower = [c.lower() for c in df.columns]
        if any("amount" in c or "sales" in c or "revenue" in c for c in cols_lower):
            for c in df.columns:
                lc = c.lower()
                if "amount" in lc or "sales" in lc or "revenue" in lc or "total" in lc:
                    res["kpis"].append({"type": "sum", "column": c, "label": f"Total {c}"})
        if any("price" in c or "ticket" in c or "avg" in c for c in cols_lower):
            for c in df.columns:
                lc = c.lower()
                if "price" in lc or "ticket" in lc:
                    res["kpis"].append({"type": "avg", "column": c, "label": f"Avg {c}"})

        # Candidate targets: heuristic ranking
        # Rank columns by: not-high-missing, adequate cardinality, predictability quick test, semantic boost
        candidate_scores = []
        for col in df.columns:
            s = df[col]
            # skip ID-like
            unique_frac = s.nunique(dropna=True) / max(1, len(s))
            if unique_frac > 0.95:
                continue
            if pct_missing(s) > 0.6:
                continue
            # compute quick predictability
            try:
                qp = quick_predictability(df, col, max_samples)
                metric = qp.get("metric", 0.0)
            except Exception:
                metric = 0.0
            # semantic boost
            boost = 0.0
            low = col.lower()
            for kw in ["target","label","y","churn","outcome","sales","revenue","price","amount"]:
                if kw in low:
                    boost += 0.08
            score = 0.3 * (1 - pct_missing(s)) + 0.4 * metric + 0.3 * (1 - unique_frac) + boost
            candidate_scores.append((col, float(score), qp))

        candidate_scores.sort(key=lambda x: x[1], reverse=True)
        for col, sc, qp in candidate_scores[:5]:
            res["candidate_targets"].append({"col": col, "score": sc, "predictability": qp})

        # Recommend model families
        # simple rules: if top candidate is categorical -> classification families
        if res["candidate_targets"]:
            top_target = res["candidate_targets"][0]
            tcol = top_target["col"]
            if is_categorical_series(df[tcol]) or (is_numeric_series(df[tcol]) and cardinality(df[tcol]) <= 15):
                # classification
                models = [
                    {"family": "tree_ensemble", "examples": ["xgboost","lightgbm","random_forest"], "reason": "handles heterogenous features, robust to missing"},
                    {"family": "linear", "examples": ["logistic_regression"], "reason": "baseline, interpretable"},
                    {"family": "nn", "examples": ["mlp"], "reason": "if large data and complex patterns"}
                ]
            else:
                models = [
                    {"family": "tree_ensemble", "examples": ["xgboost","random_forest"], "reason": "handles non-linearities"},
                    {"family": "linear", "examples": ["ridge","elasticnet"], "reason": "baseline and interpretable"},
                    {"family": "gbm", "examples": ["lightgbm","catboost"], "reason": "fast and accurate"}
                ]
        else:
            models = [{"family": "clustering", "examples": ["kmeans","dbscan"], "reason": "no clear supervised target found; try segmentation"}]

        res["recommended_models"] = models

        # include simple feature importance suggestions (mutual info)
        feature_importance = {}
        for cand in res["candidate_targets"][:2]:
            col = cand["col"]
            try:
                if is_categorical_series(df[col]) or not is_numeric_series(df[col]):
                    mi_pairs = mutual_info_with_others(df, col, top_k=10)
                    feature_importance[col] = mi_pairs
                else:
                    # numeric target: use corr with numerics
                    feature_importance[col] = corr_with_numeric(df, col, top_k=10)
            except Exception:
                feature_importance[col] = []
        res["feature_importance_candidates"] = feature_importance

        res["time_elapsed_seconds"] = time.time() - start
        return res
