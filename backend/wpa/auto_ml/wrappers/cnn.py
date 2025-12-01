from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Flatten, Dense, Dropout
from tensorflow.keras.utils import to_categorical
import numpy as np

class CNNClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, epochs=10, batch_size=32, dropout_rate=0.5):
        self.epochs = epochs
        self.batch_size = batch_size
        self.dropout_rate = dropout_rate
        self.model_ = None
        self.encoder_ = None
        self.classes_ = None

    def fit(self, X, y):
        self.encoder_ = LabelEncoder()
        y_encoded = self.encoder_.fit_transform(y)
        self.classes_ = self.encoder_.classes_
        y_categorical = to_categorical(y_encoded)

        # Reshape X for Conv1D: [samples, timesteps, features]
        X_reshaped = np.expand_dims(X, axis=2)
        n_timesteps, n_features = X_reshaped.shape[1], X_reshaped.shape[2]
        n_classes = len(self.classes_)

        self.model_ = Sequential([
            Conv1D(filters=64, kernel_size=3, activation='relu', input_shape=(n_timesteps, n_features)),
            MaxPooling1D(pool_size=2),
            Flatten(),
            Dense(128, activation='relu'),
            Dropout(self.dropout_rate),
            Dense(n_classes, activation='softmax')
        ])

        self.model_.compile(optimizer='adam',
                              loss='categorical_crossentropy',
                              metrics=['accuracy'])

        self.model_.fit(X_reshaped, y_categorical, epochs=self.epochs, batch_size=self.batch_size, verbose=0)
        return self

    def predict(self, X):
        X_reshaped = np.expand_dims(X, axis=2)
        y_pred_proba = self.model_.predict(X_reshaped)
        y_pred_encoded = tf.argmax(y_pred_proba, axis=1).numpy()
        return self.encoder_.inverse_transform(y_pred_encoded)

    def predict_proba(self, X):
        X_reshaped = np.expand_dims(X, axis=2)
        return self.model_.predict(X_reshaped)
