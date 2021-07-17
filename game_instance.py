from tetris import Tetris
from util import getEmptyActionObj
from interval import Interval
from game_config import GameConfig, HandlingConfig

class GameInstance:

    def __init__(self, gameConfig = GameConfig, handlingConfig = HandlingConfig):

        self.gameConfig = gameConfig
        self.handlingConfig = handlingConfig

        self.tet= Tetris(gameConfig=self.gameConfig, handlingConfig=handlingConfig)
        self.garbageFunc = self.tet.receiveGarbage

        self.ac = getEmptyActionObj()

        self.timer = None

    def display(self):
        pass

    def beforeLoopHook(self):
        pass

    def loop(self, garbageTarget=None, output=True):

        self.beforeLoopHook()

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
            self.timer = Interval(1/120, self.loop)
            self.timer.start()
        
    def initialize(self):
        pass

if __name__ == "__main__":
    game = GameInstance()
    game.run()