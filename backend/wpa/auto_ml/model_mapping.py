from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso, ElasticNet, BayesianRidge, HuberRegressor, PassiveAggressiveClassifier, SGDClassifier, Perceptron
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.svm import SVR, SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering, Birch, OPTICS, MeanShift, SpectralClustering, AffinityPropagation
from sklearn.mixture import GaussianMixture
from sklearn.ensemble import IsolationForest
from xgboost import XGBClassifier, XGBRegressor
from lightgbm import LGBMClassifier, LGBMRegressor
from catboost import CatBoostClassifier, CatBoostRegressor
from prophet import Prophet
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.vector_ar.var_model import VAR
from sktime.forecasting.theta import ThetaForecaster
from implicit.als import AlternatingLeastSquares

from backend.wpa.auto_ml.wrappers import DenseNeuralNetworkClassifier #, and others

MODEL_MAP = {
    # Classification
    "logistic_regression": {
        "model": LogisticRegression,
        "type": "classification",
    },
    "random_forest": {
        "model": RandomForestClassifier,
        "type": "classification",
    },
    "decision_tree": {
        "model": DecisionTreeClassifier,
        "type": "classification",
    },
    "svm": {
        "model": SVC,
        "type": "classification",
    },
    "gradient_boosting_classifier": {
        "model": GradientBoostingClassifier,
        "type": "classification",
    },
    "adaboost": {
        "model": AdaBoostClassifier,
        "type": "classification",
    },
    "k_nearest_neighbors": {
        "model": KNeighborsClassifier,
        "type": "classification",
    },
    "naive_bayes": {
        "model": GaussianNB,
        "type": "classification",
    },
    "xgboost": {
        "model": XGBClassifier,
        "type": "classification",
    },
    "lightgbm": {
        "model": LGBMClassifier,
        "type": "classification",
    },
    "catboost": {
        "model": CatBoostClassifier,
        "type": "classification",
    },
    "passive_aggressive_classifier": {
        "model": PassiveAggressiveClassifier,
        "type": "classification",
    },
    "sgd_classifier": {
        "model": SGDClassifier,
        "type": "classification",
    },
    "perceptron": {
        "model": Perceptron,
        "type": "classification",
    },

    # Regression
    "linear_regression": {
        "model": LinearRegression,
        "type": "regression",
    },
    "ridge_regression": {
        "model": Ridge,
        "type": "regression",
    },
    "lasso_regression": {
        "model": Lasso,
        "type": "regression",
    },
    "elasticnet_regression": {
        "model": ElasticNet,
        "type": "regression",
    },
    "support_vector_regression": {
        "model": SVR,
        "type": "regression",
    },
    # Note: XGBoost, LightGBM, and CatBoost also have regressors.
    # We can handle this dynamically in the service.
    "decision_tree_regressor": {
        "model": DecisionTreeRegressor,
        "type": "regression",
    },
    "bayesian_ridge": {
        "model": BayesianRidge,
        "type": "regression",
    },
    "huber_regressor": {
        "model": HuberRegressor,
        "type": "regression",
    },

    # Clustering
    "kmeans": {
        "model": KMeans,
        "type": "clustering",
    },
    "dbscan": {
        "model": DBSCAN,
        "type": "clustering",
    },
    "agglomerative_clustering": {
        "model": AgglomerativeClustering,
        "type": "clustering",
    },
    "birch": {
        "model": Birch,
        "type": "clustering",
    },
    "optics": {
        "model": OPTICS,
        "type": "clustering",
    },
    "meanshift": {
        "model": MeanShift,
        "type": "clustering",
    },
    "spectral_clustering": {
        "model": SpectralClustering,
        "type": "clustering",
    },
    "affinity_propagation": {
        "model": AffinityPropagation,
        "type": "clustering",
    },
    "gaussian_mixture_models": {
        "model": GaussianMixture,
        "type": "clustering",
    },
    "isolation_forest": {
        "model": IsolationForest,
        "type": "unsupervised", # Anomaly Detection
    },
    "linear_discriminant_analysis": {
        "model": LinearDiscriminantAnalysis,
        "type": "unsupervised",
    },
    "principal_component_analysis": {
        "model": PCA,
        "type": "unsupervised",
    },

    # Timeseries
    "prophet": {
        "model": Prophet,
        "type": "timeseries",
    },
    "arima": {
        "model": ARIMA,
        "type": "timeseries",
    },
    "sarimax": {
        "model": SARIMAX,
        "type": "timeseries",
    },
    "vector_autoregression": {
        "model": VAR,
        "type": "timeseries",
    },
    "theta_forecaster": {
        "model": ThetaForecaster,
        "type": "timeseries",
    },

    # Deep Learning (example)
    "dense_neural_network": {
        "model": DenseNeuralNetworkClassifier,
        "type": "classification", # This wrapper is a classifier
    },

    # Recommender Systems
    "als_factorization": {
        "model": AlternatingLeastSquares,
        "type": "unsupervised",
    }
}
