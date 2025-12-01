from sklearn.linear_model import (
    LogisticRegression, LinearRegression, Ridge, Lasso, ElasticNet,
    BayesianRidge, HuberRegressor, PassiveAggressiveClassifier,
    SGDClassifier, Perceptron
)
from sklearn.ensemble import (
    RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier,
    AdaBoostClassifier, IsolationForest
)
from sklearn.svm import SVR, SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import (
    KMeans, DBSCAN, AgglomerativeClustering, Birch, OPTICS,
    MeanShift, SpectralClustering, AffinityPropagation
)
from sklearn.mixture import GaussianMixture
from xgboost import XGBClassifier, XGBRegressor
from lightgbm import LGBMClassifier, LGBMRegressor
from catboost import CatBoostClassifier, CatBoostRegressor
from prophet import Prophet
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.vector_ar.var_model import VAR
from sktime.forecasting.theta import ThetaForecaster
from implicit.als import AlternatingLeastSquares

# Import the wrappers for Deep Learning models
from backend.wpa.auto_ml.wrappers import (
    DenseNeuralNetworkClassifier, LSTMForecaster, GRUForecaster,
    TransformerForecaster, CNNClassifier, Autoencoder, RNNForecaster,
    BidirectionalLSTMForecaster
)

MODEL_MAP = {
    # Classification
    "logistic_regression": {"model": LogisticRegression, "type": "classification"},
    "random_forest_classifier": {"model": RandomForestClassifier, "type": "classification"},
    "decision_tree_classifier": {"model": DecisionTreeClassifier, "type": "classification"},
    "svm_classifier": {"model": SVC, "type": "classification"},
    "gradient_boosting_classifier": {"model": GradientBoostingClassifier, "type": "classification"},
    "adaboost": {"model": AdaBoostClassifier, "type": "classification"},
    "k_nearest_neighbors": {"model": KNeighborsClassifier, "type": "classification"},
    "naive_bayes": {"model": GaussianNB, "type": "classification"},
    "xgboost_classifier": {"model": XGBClassifier, "type": "classification"},
    "lightgbm_classifier": {"model": LGBMClassifier, "type": "classification"},
    "catboost_classifier": {"model": CatBoostClassifier, "type": "classification"},
    "passive_aggressive_classifier": {"model": PassiveAggressiveClassifier, "type": "classification"},
    "sgd_classifier": {"model": SGDClassifier, "type": "classification"},
    "perceptron": {"model": Perceptron, "type": "classification"},
    "dense_neural_network": {"model": DenseNeuralNetworkClassifier, "type": "classification"},
    "convolutional_neural_network": {"model": CNNClassifier, "type": "classification"},

    # Regression
    "linear_regression": {"model": LinearRegression, "type": "regression"},
    "ridge_regression": {"model": Ridge, "type": "regression"},
    "lasso_regression": {"model": Lasso, "type": "regression"},
    "elasticnet_regression": {"model": ElasticNet, "type": "regression"},
    "svm_regressor": {"model": SVR, "type": "regression"},
    "random_forest_regressor": {"model": RandomForestRegressor, "type": "regression"},
    "xgboost_regressor": {"model": XGBRegressor, "type": "regression"},
    "lightgbm_regressor": {"model": LGBMRegressor, "type": "regression"},
    "bayesian_ridge": {"model": BayesianRidge, "type": "regression"},
    "huber_regressor": {"model": HuberRegressor, "type": "regression"},

    # Unsupervised: Clustering, Anomaly Detection, Dimensionality Reduction
    "kmeans": {"model": KMeans, "type": "clustering"},
    "dbscan": {"model": DBSCAN, "type": "clustering"},
    "agglomerative_clustering": {"model": AgglomerativeClustering, "type": "clustering"},
    "birch": {"model": Birch, "type": "clustering"},
    "optics": {"model": OPTICS, "type": "clustering"},
    "meanshift": {"model": MeanShift, "type": "clustering"},
    "spectral_clustering": {"model": SpectralClustering, "type": "clustering"},
    "affinity_propagation": {"model": AffinityPropagation, "type": "clustering"},
    "gaussian_mixture_models": {"model": GaussianMixture, "type": "clustering"},
    "isolation_forest": {"model": IsolationForest, "type": "unsupervised"},
    "linear_discriminant_analysis": {"model": LinearDiscriminantAnalysis, "type": "unsupervised"},
    "principal_component_analysis": {"model": PCA, "type": "unsupervised"},
    "als_factorization": {"model": AlternatingLeastSquares, "type": "unsupervised"},
    "autoencoder": {"model": Autoencoder, "type": "unsupervised"},
    "t_sne": {"model": TSNE, "type": "unsupervised"},

    # Timeseries
    "prophet": {"model": Prophet, "type": "timeseries"},
    "arima": {"model": ARIMA, "type": "timeseries"},
    "sarimax": {"model": SARIMAX, "type": "timeseries"},
    "vector_autoregression": {"model": VAR, "type": "timeseries"},
    "theta_forecaster": {"model": ThetaForecaster, "type": "timeseries"},
    "lstm": {"model": LSTMForecaster, "type": "timeseries"},
    "gru": {"model": GRUForecaster, "type": "timeseries"},
    "transformer": {"model": TransformerForecaster, "type": "timeseries"},
    "recurrent_neural_network": {"model": RNNForecaster, "type": "timeseries"},
    "bidirectional_lstm": {"model": BidirectionalLSTMForecaster, "type": "timeseries"},
}
