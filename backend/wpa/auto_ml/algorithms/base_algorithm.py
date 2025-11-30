class BaseAlgorithm:
    """
    Clase base abstracta para todos los algoritmos en el sistema SADI.

    Define la interfaz estándar que cada wrapper de algoritmo debe implementar,
    asegurando la interoperabilidad con el motor de AutoML.
    """
    name = "undefined"
    type = "classifier"  # O "regressor", "clustering", "anomaly", etc.

    def train(self, X, y):
        """
        Entrena el modelo con los datos proporcionados.

        Args:
            X: DataFrame de Pandas con las características.
            y: Serie de Pandas con la variable objetivo.
        """
        raise NotImplementedError

    def predict(self, X):
        """
        Realiza predicciones sobre nuevos datos.

        Args:
            X: DataFrame de Pandas con las características.

        Returns:
            Un array o Serie de Pandas con las predicciones.
        """
        raise NotImplementedError

    def metadata(self):
        """
        Devuelve metadatos sobre el algoritmo.

        Returns:
            Un diccionario con información como el nombre y el tipo.
        """
        return {
            "name": self.name,
            "type": self.type,
        }
