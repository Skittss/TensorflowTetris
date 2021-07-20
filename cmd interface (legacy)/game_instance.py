from tetris import Tetris
from util import getEmptyActionObj
from interval import Interval
from time import time

class GameInstance:

    def __init__(self, gameConfig, handlingConfig):

        self.gameConfig = gameConfig
        self.handlingConfig = handlingConfig

        self.tet= Tetris(gameConfig=self.gameConfig, handlingConfig=handlingConfig, seed=gameConfig.seed, garbageSeed=gameConfig.garbageSeed)
        self.garbageFunc = self.tet.receiveGarbage

        self.ac = getEmptyActionObj()

        self.lastTick = time()

        self.timer = None

    def display(self):
        pass

    def beforeLoopHook(self):
        pass

    def loop(self, garbageTarget=None, output=True, DEBUG=False):

        self.beforeLoopHook()

        if DEBUG:
            print(time() - self.lastTick)
            self.lastTick = time()

        goNext = self.tet.nextState(self.ac, garbageTarget=garbageTarget)

        if goNext == False:
            #self.__init__()
            return

        if output:
            self.display()

    def exit(self):
        pass

    def run(self):

        self.initialize()

        if not self.timer:
            self.timer = Interval(1/self.gameConfig.frameRate, self.loop)
            self.timer.start()
        
    def initialize(self):
        pass