import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 

from solo_env import SoloEnvironment
from ddqn import DDQN
from replay_buffer import ReplayBuffer
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.optimizers import Adam
import numpy as np
from agent_config import AgentGameConfig, AgentHandlingConfig
from datetime import datetime
import matplotlib.pyplot as plt

class SoloAgent():

    class Hyperparameters():

        # Learning Params
        batch_size = 64
        learning_rate = 1e-3
        gamma = 0.99
        n_actions = 255

        max_epsilon = 1.0
        min_epsilon = 0.02
        epsilon_decay = 1e-3

        memory_size = 100000
        dense1_dims = 100
        dense2_dims = 100

        replace_target_interval = 50

        # Training Params
        n_episodes = 8000

        log_interval = 10
        eval_interval = 1000
        n_eval_episodes = 10


    def __init__(self, gameConfig, handlingConfig, pickle_path='solo_ddqn.h5'):

        self.pickle_path = pickle_path
        self.env = SoloEnvironment(gameConfig, handlingConfig)
        self.eval_env = SoloEnvironment(gameConfig, handlingConfig)
        s, _, _ = self.env.reset()

        self.memory = ReplayBuffer(self.Hyperparameters.memory_size, s.shape)
        self.policy_q_net = DDQN(self.Hyperparameters.n_actions, self.Hyperparameters.dense1_dims, self.Hyperparameters.dense2_dims)
        self.target_q_net = DDQN(self.Hyperparameters.n_actions, self.Hyperparameters.dense1_dims, self.Hyperparameters.dense2_dims)

        self.policy_q_net.compile(optimizer=Adam(learning_rate=self.Hyperparameters.learning_rate), loss='mean_squared_error')

        self.target_q_net.compile(optimizer=Adam(learning_rate=self.Hyperparameters.learning_rate), loss='mean_squared_error')

        self.epsilon = self.Hyperparameters.max_epsilon
        self.actions = list(range(self.Hyperparameters.n_actions))

        self.learn_step = 0

    def store_transition(self, s, a, r, s_prime, t):
        self.memory.store_transition(s, a, r, s_prime, t)

    def choose_action(self, observation):

        # Do Epsilon-Greedy
        if np.random.random() < self.epsilon:
            a = np.random.choice(self.actions)
        else:
            # Choose action from advantage layer
            actions = self.policy_q_net.get_advantage(np.array([observation]))
            a = tf.math.argmax(actions, axis=1).numpy()[0]

        return a

    def learn(self):
        if self.memory.memory_count < self.Hyperparameters.batch_size:
            return

        if self.learn_step % self.Hyperparameters.replace_target_interval == 0:
            self.target_q_net.set_weights(self.policy_q_net.get_weights())

        s, a, r, s_prime, t = self.memory.sample(self.Hyperparameters.batch_size)

        q_value = self.policy_q_net(s)
        q_expected = tf.math.reduce_max(self.target_q_net(s_prime), axis=1, keepdims=True).numpy()
        q_target = np.copy(q_value)

        # Reduce terminal states to zero-value.
        for idx, v in enumerate(t):
            if v:
                q_expected[idx] = 0
            q_target[idx, a[idx]] = r[idx] + self.Hyperparameters.gamma * q_expected[idx]
        self.policy_q_net.train_on_batch(s, q_target)

        # Reduce epsilon.
        self.epsilon = max(self.Hyperparameters.min_epsilon, self.epsilon - self.Hyperparameters.epsilon_decay)

        self.learn_step += 1

    def train(self):

        returns, epsilons = [], []

        for i in range(self.Hyperparameters.n_episodes):

            s, reward, episode_finished = self.env.reset()
            while not episode_finished:
                a = self.choose_action(s)
                s_prime, r, episode_finished = self.env.step(a)
                reward += r
                # Collect data about transition
                self.store_transition(s, a, r, s_prime, episode_finished)
                s = s_prime
                self.learn()

            returns.append(reward)
            epsilons.append(self.epsilon)

            if i % self.Hyperparameters.log_interval == 0:
                avg = np.mean(returns[-10:])
                print(f"Episode: {i} \t| Instance Reward: {reward} \t| 10-Rolling Avg: {avg} \t| Epsilon {self.epsilon:.3f}")

        self.plot_data(returns, epsilons)
        self.save()
        print("Training Finished.")

    def plot_data(self, returns, epsilons):

        filename = f"{datetime.strftime('%Y-%m-%d_%H:%M')}_solo-agent_n={self.Hyperparameters.n_episodes}"
        x = [i+1 for i in range(self.Hyperparameters.n_episodes)]

        fig=plt.figure()
        ax=fig.add_subplot(111, label="1")
        ax2=fig.add_subplot(111, label="2", frame_on=False)

        ax.plot(x, epsilons, color="C0")
        ax.set_xlabel("Episode", color="C0")
        ax.set_ylabel("Epsilon", color="C0")
        ax.tick_params(axis='x', colors="C0")
        ax.tick_params(axis='y', colors="C0")

        N = len(returns)
        running_avg = np.empty(N)
        for t in range(N):
            running_avg[t] = np.mean(returns[max(0, t-20):(t+1)])

        ax2.scatter(x, running_avg, color="C1")
        ax2.axes.get_xaxis().set_visible(False)
        ax2.yaxis.tick_right()
        ax2.set_ylabel('Rewards', color="C1")
        ax2.yaxis.set_label_position('right')
        ax2.tick_params(axis='y', colors="C1")

        plt.savefig(filename)

    def save(self):
        self.target_q_net.save(self.pickle_path)

    def load(self):
        self.target_q_net = keras.models.load_model(self.pickle_path)

if __name__ == "__main__":
    solo_agent = SoloAgent(AgentGameConfig, AgentHandlingConfig)
    solo_agent.train()