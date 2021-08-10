import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.optimizers import Adam
import numpy as np


class DDQN(keras.Model):

    def __init__(self, n_actions, dense1_dims, dense2_dims):
        super().__init__()
        self.dense1 = keras.layers.Dense(dense1_dims, activation='relu')
        self.dense2 = keras.layers.Dense(dense2_dims, activation='relu')

        self.value_layer = keras.layers.Dense(1, activation=None)
        self.advantage_layer = keras.layers.Dense(n_actions, activation=None)

    # Feed forward 
    def call(self, state):
        
        feed_dense = self.dense2(self.dense1(state))
        feed_value = self.value_layer(feed_dense)
        feed_advantage = self.advantage_layer(feed_dense)

        # Combine value & advantage layer
        feed_q = (feed_value + (feed_advantage - tf.math.reduce_mean(feed_advantage, axis=1, keepdims=True)))

        return feed_q

    # For choosing actions.
    def get_advantage(self, state):

        feed_dense = self.dense2(self.dense1(state))
        return self.advantage_layer(feed_dense)
