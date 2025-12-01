from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import SimpleRNN, Dense, Dropout
from ._base_dl_wrapper import BaseDeepLearningForecaster

class RNNForecaster(BaseDeepLearningForecaster):
    def __init__(self, epochs=20, batch_size=32, window_size=5, rnn_units=50):
        super().__init__(epochs=epochs, batch_size=batch_size, window_size=window_size)
        self.rnn_units = rnn_units

    def _build_model(self, n_features):
        model = Sequential([
            SimpleRNN(self.rnn_units, activation='relu', input_shape=(self.window_size, n_features)),
            Dropout(0.2),
            Dense(1)
        ])
        return model
