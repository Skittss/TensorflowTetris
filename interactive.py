from tetris import Tetris, Action, getEmptyActionObj
from time import sleep
from interval import Interval
import os
import sys
from colorama import init, Fore, Back, Style
from pynput import keyboard
import cursor

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

        self.keybindings = {
            Action.Left:            keyboard.Key.left,
            Action.Right:           keyboard.Key.right,
            Action.SoftDrop:        keyboard.Key.down,
            Action.HardDrop:        keyboard.Key.space,
            Action.RotateLeft:      keyboard.Key.up,
            Action.RotateRight:     'z',
            Action.Rotate180:       'x',
            Action.Hold:            'c'
        }

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

    def __formatString(self, string):

        for k in self.escapeChars:
            string = string.replace(k, f"{self.escapeChars[k]}{k}")+Style.RESET_ALL

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
        # bugstr = "\n"

        # for k in self.keyInfo:
        #     bugstr += f"{k} | {self.keyInfo[k]}\n"

        count = display.count('\n') # + bugstr.count('\n')
        # print(bugstr)
        # count+=1
        sys.stdout.flush()
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

    def run(self):
        #keyboard.on_press_key("space", lambda *args: self.__bufferHardDrop())

        os.system('cls')
        cursor.hide_cursor()

        if not self.timer:
            # self.timer = RepeatedTimer(0.01, self.__loop)
            self.timer = Interval(0.01, self.__loop)
            self.timer.start()
            
        with keyboard.Listener(on_press = self.__on_press, on_release=self.__on_release) as listener:
            listener.join()


# init()
# tet = Tetris()
# escapeChars = {
#     "0": Fore.BLACK,
#     "1": Fore.CYAN,
#     "2": Fore.BLUE,
#     "3": Fore.YELLOW,
#     "4": Fore.LIGHTYELLOW_EX,
#     "5": Fore.GREEN,
#     "6": Fore.MAGENTA,
#     "7": Fore.RED
# }

# ac = getEmptyActionObj()

# def setActionParamTrue(param):
#     ac[param] = True

# keyboard.on_press_key("space", lambda *args: setActionParamTrue(Action.HardDrop))

# def formatString(string):

#     string = "\n\n " + string.replace('[',"").replace(']',"").replace('.',"")

#     for k in escapeChars:
#         string = string.replace(k, f"{escapeChars[k]}{k}")+Style.RESET_ALL

#     return string

# def getActionFromInputs(ac):
    
#     if (keyboard.is_pressed("left")):
#         ac[Action.Left] = True

#     if (keyboard.is_pressed("right")):
#         ac[Action.Right] = True

#     if (keyboard.is_pressed("down")):
#         ac[Action.SoftDrop] = True

#     if (keyboard.is_pressed("up")):
#         ac[Action.RotateLeft] = True
    
#     if (keyboard.is_pressed("z")):
#         ac[Action.RotateRight] = True

#     if (keyboard.is_pressed("x")):
#         ac[Action.Rotate180] = True

#     if (keyboard.is_pressed("c")):
#         ac[Action.Hold] = True

#     # if (keyboard.is_pressed("space")):
#     #     ac[Action.HardDrop] = True

#     return ac

# # while True:
# #     try:
# #         ac = getActionFromInputs(ac)

# #         tet.nextState(ac)

# #         display = formatString(str(tet))

# #         count = display.count('\n')
# #         print(display, end=f"\x1b[{count}A")

# #         ac = getEmptyActionObj()
# #         sleep(0.03)

# #     except KeyboardInterrupt:
# #         break

# def loop(ac):
#     ac = getActionFromInputs(ac)

#     tet.nextState(ac)

#     display = formatString(str(tet))

#     count = display.count('\n')
#     print(display, end=f"\x1b[{count}A")

#     ac = getEmptyActionObj()
    
#     return ac

# if __name__ == "__main__":
#     os.system('cls')
#     cursor.hide_cursor()

#     timer = RepeatedTimer(0.1, loop, ac)

if __name__ == "__main__":
    game = Interactive()
    game.run()