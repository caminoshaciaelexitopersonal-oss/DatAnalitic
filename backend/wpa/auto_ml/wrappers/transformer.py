from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Dropout, LayerNormalization, MultiHeadAttention, GlobalAveragePooling1D
from ._base_dl_wrapper import BaseDeepLearningForecaster
import tensorflow as tf

class TransformerEncoder(tf.keras.layers.Layer):
    def __init__(self, embed_dim, num_heads, ff_dim, rate=0.1):
        super(TransformerEncoder, self).__init__()
        self.att = MultiHeadAttention(num_heads=num_heads, key_dim=embed_dim)
        self.ffn = tf.keras.Sequential(
            [Dense(ff_dim, activation="relu"), Dense(embed_dim),]
        )
        self.layernorm1 = LayerNormalization(epsilon=1e-6)
        self.layernorm2 = LayerNormalization(epsilon=1e-6)
        self.dropout1 = Dropout(rate)
        self.dropout2 = Dropout(rate)

    def call(self, inputs, training):
        attn_output = self.att(inputs, inputs)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(inputs + attn_output)
        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        return self.layernorm2(out1 + ffn_output)

class TransformerForecaster(BaseDeepLearningForecaster):
    def __init__(self, epochs=20, batch_size=32, window_size=5, num_heads=2, ff_dim=32):
        super().__init__(epochs=epochs, batch_size=batch_size, window_size=window_size)
        self.num_heads = num_heads
        self.ff_dim = ff_dim

    def _build_model(self, n_features):
        inputs = Input(shape=(self.window_size, n_features))
        # The TransformerEncoder expects a certain embedding dimension.
        # We can use a Dense layer to project n_features to a fixed dimension if needed.
        # For simplicity, we'll assume the model can handle the feature dimension directly.
        embed_dim = n_features

        transformer_block = TransformerEncoder(embed_dim, self.num_heads, self.ff_dim)
        x = transformer_block(inputs)
        x = GlobalAveragePooling1D()(x)
        x = Dropout(0.1)(x)
        x = Dense(20, activation="relu")(x)
        x = Dropout(0.1)(x)
        outputs = Dense(1)(x)

        return Model(inputs=inputs, outputs=outputs)
