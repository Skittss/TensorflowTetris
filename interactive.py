from tetris import Tetris, getEmptyActionObj
from util import Action
from time import sleep
from interval import Interval
import os
import sys
from colorama import init, Fore, Style
from pynput import keyboard
import cursor
from config import Config

class Interactive:

    def __init__(self):
        init()
        self.tet= Tetris()
        self.escapeChars = {
            "0": Fore.BLACK,
            "1": Fore.CYAN,
            "2": Fore.BLUE,
            "3": Fore.YELLOW,
            "4": Fore.LIGHTYELLOW_EX,
            "5": Fore.GREEN,
            "6": Fore.MAGENTA,
            "7": Fore.RED
        }
        self.ac = getEmptyActionObj()

        self.keybindings = Config.keybindings

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

    def __formatString(self, string):

        for k in self.escapeChars:
            string = string.replace(k, f"{self.escapeChars[k]}{k}")+Style.RESET_ALL

        string = string.replace("Next:", f"{Fore.WHITE}Next:{Style.RESET_ALL}").replace("Hold:", f"{Fore.WHITE}Hold:{Style.RESET_ALL}")

        return string

    def __isActionToggled(self, action):
        return self.keyInfo[self.keybindings[action]]["cur"] and not self.keyInfo[self.keybindings[action]]["prev"]

    def __isActionDown(self, action):
        return self.keyInfo[self.keybindings[action]]["cur"]

    def __doActionCheck(self, action, checkFunc):

        if checkFunc(action):
            self.ac[action] = True
        else:
            self.ac[action] = False

    def __getActionFromInputs(self):

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

    def __loop(self):
        self.__getActionFromInputs()
        self.__forwardAllKeyStates()

        goNext = self.tet.nextState(self.ac)

        if goNext == False:
            self.__init__()
            return
        
        display = self.__formatString(str(self.tet))


        count = display.count('\n')
        #sys.stdout.flush()
        print(display, end=f"\x1b[{count}A")

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
            self.timer = Interval(1/120, self.__loop)
            self.timer.start()
            
        self.inputListener = keyboard.Listener(on_press = self.__on_press, on_release=self.__on_release)
        self.inputListener.start()

        self.exitListener = keyboard.GlobalHotKeys({'<ctrl>+<shift>': self.stopThreads})
        self.exitListener.start()

if __name__ == "__main__":
    game = Interactive()
    game.run()