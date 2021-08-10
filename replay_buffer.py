import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.optimizers import Adam
import numpy as np

class ReplayBuffer():

    def __init__(self, memory_size, input_shape):
        self.memory_size = memory_size
        self.memory_count = 0

        self.state_memory = np.zeros((self.memory_size, *input_shape), dtype=np.float32)
        self.next_state_memory = np.zeros((self.memory_size, *input_shape), dtype=np.float32)

        self.action_memory = np.zeros(self.memory_size, dtype=np.int32)
        self.reward_memory = np.zeros(self.memory_size, dtype=np.float32)
        self.terminal_memory = np.zeros(self.memory_size, dtype=np.bool)

    def store_transition(self, s, a, r, s_prime, t):
        idx = self.memory_count % self.memory_size  # Next free memory slot, wrap around when memory goes over max.
        self.state_memory[idx] = s
        self.action_memory[idx] = a
        self.reward_memory[idx] = r
        self.next_state_memory[idx] = s_prime
        self.terminal_memory[idx] = t

        self.memory_count += 1

    def sample(self, batch_size):

        sample_end = min(self.memory_size, self.memory_count)
        batch = np.random.choice(sample_end, batch_size, replace=False) # Don't sample the same memory twice

        s = self.state_memory[batch]
        s_prime = self.next_state_memory[batch]
        a = self.action_memory[batch]
        r = self.reward_memory[batch]
        t = self.terminal_memory[batch]

        return s, a, r, s_prime, t