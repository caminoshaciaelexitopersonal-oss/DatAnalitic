import os
import json
import math
import time
import hashlib
import warnings
from typing import Dict, List, Any, Optional

import pandas as pd
import numpy as np

# sklearn imports used in quick predict
from sklearn.model_selection import cross_val_score, StratifiedKFold, KFold
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.compose import ColumnTransformer
from sklearn.utils import resample

# Optional: mutual_info_score
from sklearn.feature_selection import mutual_info_classif, mutual_info_regression
from scipy import stats

warnings.filterwarnings("ignore")

# --------------------------
# Default configuration
# --------------------------
DEFAULT_CONFIG = {
    "weights": {"A": 0.15, "T": 0.10, "V": 0.10, "R": 0.20, "P": 0.45, "S": 0.05, "O": 0.20}, # Increased weight for Predictability
    "thresholds": {"confirm_score": 0.65, "gap_threshold": 0.10}, # Lowered thresholds for testing
    "quick_predict": {
        "min_sample_for_pred": 200,
        "max_sample_for_pred": 5000,
        "top_k_predictors": 10,
        "cv_folds": 3,
        "random_state": 42
    },
    "limits": {
        "max_unique_as_id_fraction": 0.95,
        "max_id_string_length": 3
    },
    "semantic_keywords": ["target", "label", "y", "outcome", "resultado", "respuesta", "churn", "venta", "price", "amount", "score", "value"]
}

# --------------------------
# Utilities
# --------------------------
def sha256_of_file(path: str, chunk_size: int = 65536) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()

def save_json_atomic(path: str, obj: Any):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, path)

def safe_mkdir(path: str):
    os.makedirs(path, exist_ok=True)

# --------------------------
# Column heuristics
# --------------------------
def is_id_column(series: pd.Series, config: Dict = DEFAULT_CONFIG) -> bool:
    """Detects columns type ID: high uniqueness and long values or integers with high cardinality."""
    n = len(series)
    if n == 0:
        return False
    nunique = series.nunique(dropna=True)
    unique_frac = nunique / float(n)
    # If too many unique values -> likely ID
    if unique_frac >= config["limits"]["max_unique_as_id_fraction"]:
        # If strings and average length > threshold or numeric ints -> ID
        if pd.api.types.is_object_dtype(series):
            avg_len = series.dropna().astype(str).map(len).mean() if nunique > 0 else 0
            if avg_len >= config["limits"]["max_id_string_length"]:
                return True
        if pd.api.types.is_integer_dtype(series) or pd.api.types.is_float_dtype(series):
            return True
    return False

def semantic_boost(col_name: str, config: Dict = DEFAULT_CONFIG) -> float:
    name = str(col_name).lower()
    for kw in config["semantic_keywords"]:
        if kw in name:
            return 0.08 # small default boost
    return 0.0

# --------------------------
# Scoring components
# --------------------------
def availability_score(series: pd.Series) -> float:
    pct_missing = series.isna().mean() if len(series) > 0 else 1.0
    return max(0.0, 1.0 - pct_missing)

def type_score(series: pd.Series) -> float:
    if pd.api.types.is_numeric_dtype(series):
        n_unique = series.nunique(dropna=True)
        return 1.0 if n_unique > 10 else 0.6
    if pd.api.types.is_categorical_dtype(series) or pd.api.types.is_object_dtype(series):
        n_unique = series.nunique(dropna=True)
        if 2 <= n_unique <= 50:
            return 1.0
        elif n_unique > 50:
            return 0.4
        else:
            return 0.2
    return 0.1

def variability_score(series: pd.Series, df: pd.DataFrame) -> float:
    """Normalized variability score for numeric or categorical."""
    if pd.api.types.is_numeric_dtype(series):
        var_col = float(np.nanvar(series.dropna()))
        # median var across numeric features
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(num_cols) <= 1:
            return 0.5
        median_var = float(np.nanmedian([np.nanvar(df[c].dropna()) for c in num_cols if c != series.name and df[c].dropna().shape[0] > 0] or [var_col + 1e-9]))
        score = var_col / (var_col + median_var + 1e-12)
        return float(max(0.0, min(1.0, score)))
    else:
        # categorical: balancedness
        vc = series.value_counts(normalize=True, dropna=True)
        if vc.empty:
            return 0.0
        score = 1.0 - float(vc.iloc[0]) # 1 - proportion of largest class
        return float(max(0.0, min(1.0, score)))

def correlation_signal(df: pd.DataFrame, col: str, top_k: int = 20) -> float:
    """Compute a normalized correlation signal (0..1) with other features."""
    s = df[col]
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # if target numeric: use pearson absolute values
    try:
        if pd.api.types.is_numeric_dtype(s):
            others = [c for c in numeric_cols if c != col]
            corrs = []
            for c in others:
                try:
                    corr = df[col].corr(df[c])
                    if not np.isnan(corr):
                        corrs.append(abs(corr))
                except Exception:
                    continue
            if not corrs:
                return 0.0
            corrs = sorted(corrs, reverse=True)[:top_k]
            # normalize median correlation to 0..1 via tanh-like mapping
            med = float(np.median(corrs))
            return float(max(0.0, min(1.0, med)))
        else:
            # categorical: mutual information with numeric and categorical predictors
            # use mutual_info_classif/regression heuristics
            # fallback to 0 if fails
            X = df.drop(columns=[col]).select_dtypes(include=[np.number]).fillna(0)
            y = pd.factorize(df[col].astype(str))[0]
            if X.shape[1] == 0:
                return 0.0
            try:
                mi = mutual_info_classif(X, y, discrete_features='auto')
                if len(mi) == 0:
                    return 0.0
                med = float(np.median(mi))
                # normalize roughly by logistic
                return float(max(0.0, min(1.0, med / (med + 1.0))))
            except Exception:
                return 0.0
    except Exception:
        return 0.0

def operational_penalty(series: pd.Series, col_name: str) -> float:
    """Penalize if PII suspected, huge missingness, too high cardinality for categorical, etc."""
    penalty = 0.0
    n = len(series)
    if n == 0:
        return 1.0
    pct_missing = series.isna().mean()
    if pct_missing > 0.5:
        penalty += 0.2
    # PII heuristics (very simple; should be improved with a dedicated detector)
    name = str(col_name).lower()
    if any(x in name for x in ["email", "ssn", "dni", "passport", "phone", "telefono"]):
        penalty += 0.6
    # high cardinality categorical
    if pd.api.types.is_object_dtype(series) and series.nunique(dropna=True) > 1000:
        penalty += 0.2
    return float(max(0.0, min(1.0, penalty)))

# --------------------------
# Quick predictability estimate
# --------------------------
def map_metric_to_01(metric: float, task: str = "classification") -> float:
    """Map metric to 0..1. classification: AUC baseline 0.5; regression: R2 baseline 0."""
    if task == "classification":
        # AUC range 0.5-0.95 considered useful
        if np.isnan(metric):
            return 0.0
        val = (metric - 0.5) / 0.45
        return float(max(0.0, min(1.0, val)))
    else:
        if np.isnan(metric):
            return 0.0
        # R2 can be negative; map negative to 0
        val = max(metric, 0.0)
        # assume 0..0.8 meaningful
        return float(max(0.0, min(1.0, val / 0.8)))

def select_top_k_predictors(df: pd.DataFrame, target: pd.Series, k: int = 10) -> List[str]:
    """Select top K predictors by absolute corr (numeric) or mutual info (categorical)."""
    X = df.select_dtypes(include=[np.number]).drop(columns=[target.name], errors="ignore")
    if X.shape[1] == 0:
        return []
    corrs = {}
    for c in X.columns:
        try:
            corr = abs(df[target.name].corr(df[c]))
            corrs[c] = 0.0 if np.isnan(corr) else float(corr)
        except Exception:
            corrs[c] = 0.0
    sorted_cols = sorted(corrs.items(), key=lambda x: x[1], reverse=True)
    return [c for c, _ in sorted_cols[:k]]

def quick_predictability_estimate(df: pd.DataFrame, col: str, config: Dict = DEFAULT_CONFIG) -> Dict[str, Any]:
    """
    Cheap predictive estimate:
      - sample up to max_sample_for_pred
      - select top-k predictors
      - run 3-fold CV on lightweight models (DecisionTree + Logistic/Ridge)
    Returns: {"metric": "auc"|"r2"|"na", "value": 0..1, "raw": raw_metric}
    """
    n = len(df)
    if n == 0:
        return {"metric": "na", "value": 0.0}
    qcfg = config["quick_predict"]
    min_n = qcfg["min_sample_for_pred"]
    max_n = qcfg["max_sample_for_pred"]
    sample_n = min(max_n, n)
    if n < min_n:
        # not enough data to estimate reliably
        return {"metric": "na", "value": 0.0, "note": "insufficient_rows"}

    # sample deterministically
    sample = df.sample(n=sample_n, random_state=qcfg["random_state"])
    y = sample[col]
    X = sample.drop(columns=[col])

    # select predictors
    num_X = X.select_dtypes(include=[np.number])
    top_preds = select_top_k_predictors(pd.concat([num_X, y], axis=1), y, k=qcfg["top_k_predictors"])
    if len(top_preds) == 0:
        # fallback: use all numeric columns if none selected
        top_preds = num_X.columns.tolist()[:qcfg["top_k_predictors"]]
    X_sub = X[top_preds].copy() if top_preds else pd.DataFrame(index=sample.index)

    # quick pipelines
    try:
        is_classification_task = (
            not pd.api.types.is_numeric_dtype(y) or
            y.nunique(dropna=True) <= 20  # Treat low-cardinality numeric as classification
        )

        if not is_classification_task:
            # regression quick test
            pipe = Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                ("ridge", Ridge(random_state=qcfg["random_state"]))
            ])
            cv = KFold(n_splits=qcfg["cv_folds"], shuffle=True, random_state=qcfg["random_state"])
            if X_sub.shape[1] == 0:
                return {"metric": "na", "value": 0.0, "note": "no_numeric_predictors"}
            scores = cross_val_score(pipe, X_sub, y, cv=cv, scoring="r2", error_score=np.nan)
            raw = float(np.nanmean(scores))
            mapped = map_metric_to_01(raw, task="regression")
            return {"metric": "r2", "raw": raw, "value": mapped}
        else:
            # classification quick test
            # encode y if needed
            y_enc = pd.factorize(y)[0]
            # choose a small tree and a logistic model for robustness
            pipe_lr = Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
            ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                ("lr", LogisticRegression(max_iter=200))
            ])
            # fallback to a simple decision tree over numeric predictors
            if X_sub.shape[1] == 0:
                return {"metric": "na", "value": 0.0, "note": "no_numeric_predictors"}
            pipe_dt = Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("dt", DecisionTreeClassifier(max_depth=4, random_state=qcfg["random_state"]))
            ])
            cv = StratifiedKFold(n_splits=qcfg["cv_folds"], shuffle=True, random_state=qcfg["random_state"])

            # Use balanced_accuracy as it's robust for both binary and multiclass cases
            scores = cross_val_score(pipe_dt, X_sub.fillna(0), y_enc, cv=cv, scoring="balanced_accuracy", error_score=np.nan)
            raw = float(np.nanmean(scores))

            # Map the balanced accuracy score (0..1) to our predictability score (0..1)
            # A simple mapping: 0.5 (random) -> 0, 1.0 -> 1.0
            mapped = (raw - 0.5) / 0.5 if raw > 0.5 else 0.0
            mapped = float(max(0.0, min(1.0, mapped)))

            return {"metric": "balanced_accuracy", "raw": raw, "value": mapped}
    except Exception as e:
        return {"metric": "na", "value": 0.0, "error": str(e)}

# --------------------------
# Main detector
# --------------------------
def weighted_score(components: Dict[str, float], config: Dict = DEFAULT_CONFIG) -> float:
    w = config.get("weights", DEFAULT_CONFIG["weights"])
    # components expected keys: A,T,V,R,P,S,O (O is penalty)
    score = 0.0
    for k in ("A", "T", "V", "R", "P", "S"):
        score += w.get(k, 0.0) * float(components.get(k, 0.0))
    # subtract penalty scaled by weight
    penalty = w.get("O", 0.0) * float(components.get("O", 0.0))
    final = score - penalty
    return float(max(0.0, min(1.0, final)))

def detect_target(df: pd.DataFrame, job_id: str, config: Dict = DEFAULT_CONFIG) -> Dict[str, Any]:
    """
    Main entry point. Reads a DataFrame, computes scores for each non-ID column,
    runs quick predictability checks, and returns all results as a dictionary.
    """
    # Calculate dataset hash from DataFrame content
    dataset_hash = hashlib.sha256(pd.util.hash_pandas_object(df, index=True).values).hexdigest()

    eda_summary = {
        "n_rows": len(df),
        "n_cols": len(df.columns),
        "dataset_hash": dataset_hash,
        "columns": []
    }

    candidates = []
    for col in df.columns:
        series = df[col]
        col_summary = {
            "name": col,
            "dtype": str(series.dtype),
            "n_unique": int(series.nunique(dropna=True)),
            "pct_missing": float(series.isna().mean())
        }
        eda_summary["columns"].append(col_summary)

        if is_id_column(series, config):
            continue

        A = availability_score(series)
        T = type_score(series)
        V = variability_score(series, df)
        R = correlation_signal(df, col)
        S = semantic_boost(col, config)
        O = operational_penalty(series, col)

        try:
            P_res = quick_predictability_estimate(df, col, config)
            P = float(P_res.get("value", 0.0))
        except Exception as e:
            P_res = {"metric": "na", "value": 0.0, "error": str(e)}
            P = 0.0

        comps = {"A": A, "T": T, "V": V, "R": R, "P": P, "S": S, "O": O}
        score = weighted_score(comps, config)
        candidates.append({
            "col": col,
            "score": score,
            "components": comps,
            "predict_estimate": P_res
        })

    candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)
    top = candidates[:5]

    decision = {
        "job_id": job_id,
        "decision_mode": "requires_confirmation",
        "selected_target": None,
        "confidence": 0.0,
        "candidates": top,
        "explanation": ""
    }

    if not candidates:
        decision["explanation"] = "No candidate targets detected (all columns filtered as IDs or dataset empty)."
    else:
        best = candidates[0]
        second = candidates[1] if len(candidates) > 1 else {"score": 0.0}
        cfg_th = config.get("thresholds", DEFAULT_CONFIG["thresholds"])
        if best["score"] >= cfg_th["confirm_score"] and (best["score"] - second["score"]) >= cfg_th["gap_threshold"]:
            decision["decision_mode"] = "auto"
            decision["selected_target"] = best["col"]
            decision["confidence"] = float(best["score"])
            decision["explanation"] = f"Auto-selected {best['col']} with score {best['score']:.3f} (gap {best['score'] - second['score']:.3f})."
        else:
            decision["decision_mode"] = "requires_confirmation"
            decision["selected_target"] = None
            decision["confidence"] = float(best["score"])
            decision["explanation"] = "Top candidates require user confirmation due to low confidence or small gap."

    return {
        "target_decision": decision,
        "eda_summary": eda_summary,
        "dataset_hash": dataset_hash
    }

# --------------------------
# If used as script (for local debug)
# --------------------------
if __name__ == "__main__":
    # This part is for local testing and will not be used in the main pipeline
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="path to unified CSV")
    parser.add_argument("--job_id", required=True, help="job id")
    args = parser.parse_args()

    input_df = pd.read_csv(args.input)
    res = detect_target(input_df, args.job_id)

    print(json.dumps(res, indent=2, ensure_ascii=False))
