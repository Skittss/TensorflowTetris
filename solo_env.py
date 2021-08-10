from util import getEmptyActionObj, Action
import tensorflow as tf
import numpy as np

from tetris import Tetris
from tensorflow import one_hot

tf.compat.v1.enable_v2_behavior()

class SoloEnvironment():

    def __init__(self, gameConfig, agentHandlingConfig, maxDrops = 500):

        self.gameConfig = gameConfig
        self.agentHandlingConfig = agentHandlingConfig
        self.maxDrops = maxDrops
        self.__gameInstance = Tetris(self.gameConfig, self.agentHandlingConfig)
        self.seeds = self.__gameInstance.getSeeds()

        self.state = self.__gameInstance.getState()

        self._episode_ended = False


    def reset(self):
        self.__gameInstance = Tetris(self.gameConfig, self.agentHandlingConfig)
        self.seeds = self.__gameInstance.getSeeds()
        self.__setStateFromGame()
        self._episode_ended = False
        return self.state, 0, False

    def step(self, action):

        # if self._episode_ended:
        #     return self.reset()

        self._episode_ended, (reward, piece_count) = self.__gameInstance.nextState(self.__getGameAction(action))
        for _ in range(9):
            self._episode_ended, (new_reward, piece_count) = self.__gameInstance.nextState(self.__getGameAction(0))
            reward += new_reward

        self._episode_ended = not self._episode_ended

        self.__setStateFromGame()

        if self._episode_ended:
            return self.state, -40 + reward, True

        elif piece_count >= self.maxDrops:

            return self.state, reward, True

        else:
            return self.state, reward, False

    def __setStateFromGame(self):
        grid, extra = self.__gameInstance.getState() 
        self.state = np.asarray(grid + self.__oneHotBag(self.__gameInstance.getBagPreview()) + extra)

    def __oneHotBag(self, bag):
        return one_hot(bag, 7).numpy().flatten().tolist()

    def __getGameAction(self, action):

        permutations = [int(v) for v in list(bin(action)[2:])]

        ac = getEmptyActionObj()
        for i in range(len(permutations)):
            ac[Action(i)] = permutations[i]

        return ac