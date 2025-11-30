"""
Registro Centralizado de Algoritmos.

Este archivo descubre y registra todas las implementaciones de algoritmos
disponibles en el módulo `algorithms`. El `ALGORITHM_REGISTRY` es utilizado
por el motor de AutoML para instanciar y ejecutar los modelos.

Para añadir un nuevo algoritmo, impórtelo aquí y añádalo a la lista
en el diccionario `ALGORITHM_REGISTRY`.
"""

# --- INSTRUCCIÓN PARA JULES (FASE 2) ---
# Aquí es donde importarás cada una de las 52 clases de algoritmos.
# Ejemplo:
# from .random_forest_classifier import RandomForestClassifierAlgorithm
# from .svm_classifier import SVMClassifierAlgorithm

ALGORITHM_REGISTRY = {
    # --- INSTRUCCIÓN PARA JULES (FASE 2) ---
    # La lista de clases de algoritmos se poblará aquí.
    # cls.name: cls
    # for cls in [
    #     RandomForestClassifierAlgorithm(),
    #     SVMClassifierAlgorithm(),
    #     ...
    # ]
}

def get_algorithm(name: str, **params):
    """
    Factory function para obtener una instancia de un algoritmo del registro.
    """
    if name not in ALGORITHM_REGISTRY:
        raise ValueError(f"Algoritmo '{name}' no encontrado en el registro.")

    algorithm_class = ALGORITHM_REGISTRY[name]
    return algorithm_class(**params)
