from typing import Dict, Type, Any
from backend.wpa.auto_ml.models._base import BaseModelWrapper

# The MODEL_REGISTRY will store mappings from a model's string key to its wrapper class.
MODEL_REGISTRY: Dict[str, Type[BaseModelWrapper]] = {}

def register_model(name: str):
    """
    A decorator to register a new model wrapper in the MODEL_REGISTRY.

    This allows for a plug-and-play architecture where new models can be
    added to the system by simply decorating their wrapper class.

    Args:
        name (str): The unique key for the model, e.g., 'logistic_regression'.

    Returns:
        A decorator function.

    Example:
        @register_model('logistic_regression')
        class LogisticRegressionWrapper(BaseModelWrapper):
            ...
    """
    def decorator(cls: Type[BaseModelWrapper]):
        if name in MODEL_REGISTRY:
            raise ValueError(f"Model with name '{name}' is already registered.")
        if not issubclass(cls, BaseModelWrapper):
            raise TypeError("Registered class must be a subclass of BaseModelWrapper.")

        MODEL_REGISTRY[name] = cls
        return cls
    return decorator

def get_model(name: str, params: Dict[str, Any] = None) -> BaseModelWrapper:
    """
    Instantiates and returns a model wrapper from the registry.

    Args:
        name (str): The key of the model to retrieve.
        params (Dict[str, Any]): Parameters to pass to the model's constructor.

    Returns:
        An instance of the requested BaseModelWrapper.

    Raises:
        ValueError: If the requested model name is not in the registry.
    """
    if name not in MODEL_REGISTRY:
        raise ValueError(f"Model '{name}' not found in the registry. Available models are: {list(MODEL_REGISTRY.keys())}")

    model_class = MODEL_REGISTRY[name]
    return model_class(params=params)
