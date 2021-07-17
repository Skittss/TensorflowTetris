from interval import Interval
from interactive import Interactive 
import os
import cursor
from config import InteractiveConfig, HandlingConfig, GameConfig
from pynput import keyboard

class Multiplayer:
    
    def __init__(self, gameConfig, p1InteractiveConfig, p2InteractiveConfig, p1HandlingConfig, p2HandlingConfig):

        self.p1 = Interactive(gameConfig, p1InteractiveConfig, p1HandlingConfig)
        self.p2 = Interactive(gameConfig, p2InteractiveConfig, p2HandlingConfig)

        self.timer = None
        self.shortcutListener = None

    def start(self):

        os.system('cls')
        cursor.hide_cursor()

        self.p1.initialize(listenForShortcuts=False)
        self.p2.initialize(listenForInputs=False, listenForShortcuts=False)

        if not self.timer:
            self.timer = Interval(1/120, self.doLoops)
            self.timer.start()

        if not self.shortcutListener:
            self.shortcutListener = keyboard.GlobalHotKeys({'<ctrl>+<shift>': self.stopThreads, '<shift>+<tab>': cursor.hide_cursor})
            self.shortcutListener.start()

    def stopThreads(self):

        self.p1.stopThreads()
        self.p2.stopThreads()

        if self.timer:
            self.timer.cancel()

        if self.shortcutListener:
            self.shortcutListener.stop()

    def doLoops(self, output=True):

        self.p1.loop(output=False, garbageTarget=self.p2.garbageFunc)
        self.p2.loop(output=False, garbageTarget=self.p1.garbageFunc)

        if output:
            string, carriageReturns = self.toString()

            carriageReturns = string.count('\n')
            print(string, end=f"\x1b[{carriageReturns}A")


    def toString(self):

        str1 = self.p1.toString().split("\n")
        str2 = self.p2.toString().split("\n")

        maxlen = max(len(str1), len(str2))

        combined = "\n".join([str1[i] + str2[i] for i in range(maxlen)])

        return combined, maxlen

if __name__ == "__main__":

    g = Multiplayer(GameConfig, InteractiveConfig, InteractiveConfig, HandlingConfig, HandlingConfig)
    g.start()