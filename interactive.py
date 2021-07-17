from tetris import Tetris, getEmptyActionObj
from util import Action, KeyIcons
from time import sleep, time
from interval import Interval
import os
import sys
from colorama import init, Fore, Style
from pynput import keyboard
import cursor
from config import GameConfig, HandlingConfig, InteractiveConfig

class Interactive:

    def __init__(self, gameConfig = GameConfig, interactiveConfig = InteractiveConfig, handlingConfig = HandlingConfig):
        init()
        self.gameConfig = gameConfig
        self.interactiveConfig = interactiveConfig
        self.handlingConfig = handlingConfig

        self.tet= Tetris(gameConfig=self.gameConfig, handlingConfig=handlingConfig)
        self.garbageFunc = self.tet.receiveGarbage

        self.ac = getEmptyActionObj()

        self.keybindings = self.interactiveConfig.keybindings

        self.keyInfo = {
            self.keybindings[Action.Left]:          {"prev": False, "cur": False},
            self.keybindings[Action.Right]:         {"prev": False, "cur": False},
            self.keybindings[Action.SoftDrop]:      {"prev": False, "cur": False},
            self.keybindings[Action.HardDrop]:      {"prev": False, "cur": False},
            self.keybindings[Action.RotateLeft]:    {"prev": False, "cur": False},
            self.keybindings[Action.RotateRight]:   {"prev": False, "cur": False},
            self.keybindings[Action.Rotate180]:     {"prev": False, "cur": False},
            self.keybindings[Action.Hold]:          {"prev": False, "cur": False}

        }
        self.timer = None
        self.inputListener = None
        self.exitListener = None

    def __colourActiveInputs(self, string):
        for k in KeyIcons.entries:
            if self.ac[k]:
                string = string.replace(f"\"{KeyIcons.entries[k]}\"", f"{self.interactiveConfig.actionHighlightStyle}{KeyIcons.entries[k]}{Style.RESET_ALL}")
            else:
                string = string.replace(f"\"{KeyIcons.entries[k]}\"", f"{KeyIcons.entries[k]}")

        return string

    def __formatString(self, string):

        for k in self.interactiveConfig.pieceStyles:
            replaceString = self.interactiveConfig.pieceStyles[k] + k + Style.RESET_ALL
            string = string.replace(k, replaceString)

        string = string.replace(self.interactiveConfig.ghostCharacter, f"{self.interactiveConfig.ghostPieceStyle}{self.interactiveConfig.ghostCharacter}{Style.RESET_ALL}")

        return string

    def __formatDropPrompt(self, key, scoreString):
        
        if key == None:
            return "\n" + " "*len(scoreString)

        try:
            prompt = self.interactiveConfig.promptTable[key]

        except KeyError:
            return "\n"

        prompt += f" ({self.gameConfig.scoreTable[key]})"
        
        line = " "*int(len(scoreString) // 2 - len(prompt) // 2) + prompt
        line += " "*(len(scoreString) - len(line))

        return "\n" + line

    def __isActionToggled(self, action):
        return self.keyInfo[self.keybindings[action]]["cur"] and not self.keyInfo[self.keybindings[action]]["prev"]

    def __isActionDown(self, action):
        return self.keyInfo[self.keybindings[action]]["cur"]

    def __doActionCheck(self, action, checkFunc):

        if checkFunc(action):
            self.ac[action] = True
        else:
            self.ac[action] = False

    def getActionFromInputs(self):

        self.__doActionCheck(Action.Left, self.__isActionDown) 

        self.__doActionCheck(Action.Right, self.__isActionDown)

        self.__doActionCheck(Action.SoftDrop, self.__isActionDown)

        self.__doActionCheck(Action.RotateLeft, self.__isActionToggled)
        
        self.__doActionCheck(Action.RotateRight, self.__isActionToggled)

        self.__doActionCheck(Action.Rotate180, self.__isActionToggled)

        self.__doActionCheck(Action.Hold, self.__isActionToggled) 
  
        self.__doActionCheck(Action.HardDrop, self.__isActionToggled)

    def __forwardAllKeyStates(self):

        for k in self.keyInfo:
            self.keyInfo[k]["prev"] = self.keyInfo[k]["cur"]

    def toString(self):
        mainStr, scoreStr, actionType, actionStr, _ = self.tet.toString(GHOSTCHARACTER=self.interactiveConfig.ghostCharacter)
        actionStr = self.__colourActiveInputs(actionStr)
        
        display = self.__formatString(mainStr) + "\n" + scoreStr + self.__formatDropPrompt(actionType, scoreStr) + "\n\n" + actionStr

        return display

    def loop(self, garbageTarget=None, output=True):

        self.getActionFromInputs()
        self.__forwardAllKeyStates()

        goNext = self.tet.nextState(self.ac, garbageTarget=garbageTarget)

        if goNext == False:
            #self.__init__()
            return

        if output:

            display = self.toString()

            count = display.count('\n')
            print(display, end=f"\x1b[{count}A")    # print is current performance bottleneck. Limits framerate to effectively 10fps. Perhaps consider only re printing the characters which change?

    def __getKeyInfoDictKey(self, key):

        try:
            k = key.char

        except AttributeError:
            k = key

        return k

    def __on_press(self, key):

        dictKey = self.__getKeyInfoDictKey(key)
        
        try: 
            keyEntry = self.keyInfo[dictKey]
            if keyEntry:
                keyEntry["prev"] = keyEntry["cur"]
                keyEntry["cur"] = True

        except KeyError: 
            return

    def __on_release(self, key):
        
        dictKey = self.__getKeyInfoDictKey(key)

        try: 
            keyEntry = self.keyInfo[dictKey]
            if keyEntry:
                keyEntry["prev"] = keyEntry["cur"]
                keyEntry["cur"] = False

        except KeyError:
            return

    def stopThreads(self):
            
        if self.timer:
            self.timer.cancel()

        if self.inputListener:
            self.inputListener.stop()

        if self.exitListener:
            self.exitListener.stop()

        os.system('cls')
        cursor.show_cursor()
        quit()

    def run(self):

        os.system('cls')
        cursor.hide_cursor()

        if not self.timer:
            self.timer = Interval(1/120, self.loop)
            self.timer.start()
        
        self.initialize()

    def initialize(self, listenForInputs=True, listenForShortcuts=True):

        if listenForInputs:

            self.inputListener = keyboard.Listener(on_press = self.__on_press, on_release=self.__on_release)
            self.inputListener.start()

        if listenForShortcuts:

            self.exitListener = keyboard.GlobalHotKeys({'<ctrl>+<shift>': self.stopThreads, '<shift>+<tab>': cursor.hide_cursor})
            self.exitListener.start()

if __name__ == "__main__":
    game = Interactive()
    game.run()