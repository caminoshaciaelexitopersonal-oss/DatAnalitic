# This file is used to import all the model wrappers so that they can be
# registered in the MODEL_REGISTRY.

# Classifiers
from backend.wpa.auto_ml.models.linear_models import LogisticRegressionWrapper
from backend.wpa.auto_ml.models.tree_models import RandomForestClassifierWrapper, DecisionTreeClassifierWrapper
from backend.wpa.auto_ml.models.ensemble_models import GradientBoostingClassifierWrapper
from backend.wpa.auto_ml.models.svm_models import SVCWrapper
from backend.wpa.auto_ml.models.knn import KNeighborsClassifierWrapper
from backend.wpa.auto_ml.models.naive_bayes import GaussianNBWrapper
from backend.wpa.auto_ml.models.ensemble_models import LightGBMClassifierWrapper, XGBoostClassifierWrapper

# Regressors
from backend.wpa.auto_ml.models.linear_models import LinearRegressionWrapper, ElasticNetWrapper, LassoWrapper, RidgeWrapper
from backend.wpa.auto_ml.models.tree_models import RandomForestRegressorWrapper, ExtraTreesRegressorWrapper
from backend.wpa.auto_ml.models.svm_models import SVRWrapper
from backend.wpa.auto_ml.models.ensemble_models import GradientBoostingRegressorWrapper, LightGBMRegressorWrapper, XGBoostRegressorWrapper

# Clustering
from backend.wpa.auto_ml.models.clustering import KMeansWrapper, DBSCANWrapper, AgglomerativeClusteringWrapper, BirchWrapper, GaussianMixtureWrapper, MiniBatchKMeansWrapper
