from sklearn.base import BaseEstimator, TransformerMixin
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense

class Autoencoder(BaseEstimator, TransformerMixin):
    def __init__(self, epochs=10, batch_size=32, encoding_dim=3):
        self.epochs = epochs
        self.batch_size = batch_size
        self.encoding_dim = encoding_dim
        self.model_ = None
        self.encoder_ = None

    def fit(self, X, y=None):
        n_features = X.shape[1]

        input_layer = Input(shape=(n_features,))
        encoded = Dense(128, activation='relu')(input_layer)
        encoded = Dense(64, activation='relu')(encoded)
        encoded = Dense(self.encoding_dim, activation='relu')(encoded)

        decoded = Dense(64, activation='relu')(encoded)
        decoded = Dense(128, activation='relu')(decoded)
        decoded = Dense(n_features, activation='sigmoid')(decoded)

        self.model_ = Model(input_layer, decoded)
        self.encoder_ = Model(input_layer, encoded)

        self.model_.compile(optimizer='adam', loss='mean_squared_error')
        self.model_.fit(X, X, epochs=self.epochs, batch_size=self.batch_size, shuffle=True, verbose=0)

        return self

    def transform(self, X):
        return self.encoder_.predict(X)

    def fit_transform(self, X, y=None):
        self.fit(X)
        return self.transform(X)

    # Required for scikit-learn pipeline compatibility
    def predict(self, X):
        # In a clustering context, this would return cluster labels.
        # For a simple autoencoder, we return the reconstruction error.
        reconstructed = self.model_.predict(X)
        mse = ((X - reconstructed) ** 2).mean(axis=1)
        # Simple anomaly detection: return 1 for high error, 0 for low
        threshold = mse.mean() + mse.std()
        return (mse > threshold).astype(int)
