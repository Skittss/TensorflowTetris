from game_instance import GameInstance
from util import Action, KeyIcons
import os
from colorama import init, Fore, Style
from pynput import keyboard
import cursor
from game_config import GameConfig, HandlingConfig
from cmd_interactive_config import CmdInteractiveConfig
import numpy as np

class CmdInstance(GameInstance):

    def __init__(self, gameConfig = GameConfig, interactiveConfig = CmdInteractiveConfig, handlingConfig = HandlingConfig):
        super().__init__(gameConfig=gameConfig, handlingConfig=handlingConfig)
        init()  # Colorama

        self.interactiveConfig = interactiveConfig

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

        self.inputListener = None
        self.exitListener = None

    def display(self):
        display = self.toString()

        count = display.count('\n')
        print(display, end=f"\x1b[{count}A")

    def initialize(self, listenForInputs=True, listenForShortcuts=True):

        os.system('cls')
        cursor.hide_cursor()

        if listenForInputs:

            self.inputListener = keyboard.Listener(on_press = self.__on_press, on_release=self.__on_release)
            self.inputListener.start()

        if listenForShortcuts:

            self.exitListener = keyboard.GlobalHotKeys({'<ctrl>+<shift>': self.exit, '<shift>+<tab>': cursor.hide_cursor})
            self.exitListener.start()

    def beforeLoopHook(self):

        self.__getActionFromInputs()
        self.__forwardAllKeyStates()

    def exit(self):

        if self.timer:
            self.timer.cancel()

        if self.inputListener:
            self.inputListener.stop()

        if self.exitListener:
            self.exitListener.stop()

        os.system('cls')
        cursor.show_cursor()
        quit()

    ########################################################################### String Manipulation
        
    def toString(self):
        mainStr, scoreStr, actionType, actionStr, _ = self.tetrisToString(self.tet.getDisplayData(), GHOSTCHARACTER=self.interactiveConfig.ghostCharacter)
        actionStr = self.__colourActiveInputs(actionStr)
        
        display = self.__formatString(mainStr) + "\n" + scoreStr + self.__formatDropPrompt(actionType, scoreStr) + "\n\n" + actionStr

        return display

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

    def __gridToStringList(self, displayData, garbageCharacter):

        return [[str(int(v)) if not v == displayData.garbageValue else garbageCharacter for v in row] for row in displayData.grid[displayData.hiddenRows:]]

    def tetrisToString(self, displayData, MINPAD = 5, EXTRAPAD = 10, UIVERTICALPAD = 1, PIECEPAD = 1, ACTIONVERTPAD = 4, COMBOROW = 7, SHOWGHOST = True, GHOSTCHARACTER = "@", GARBAGECHARACTER = "#", DEBUG = False):

        # Get rid of all the garbage from numpy str
        string = self.__gridToStringList(displayData, GARBAGECHARACTER)

        # Add ghost piece:

        if SHOWGHOST and not displayData.lost:
            ghostPos = displayData.ghostPos

            for i in range(0, len(displayData.currentTetrominoMatrix)):
                matrixRow = displayData.currentTetrominoMatrix[i]
                try:
                    row = string[ghostPos[0, 1] + i]

                    for (j,), v in np.ndenumerate(matrixRow):
                        if not v == 0 and row[ghostPos[0, 0] + j] == "0":
                            row[ghostPos[0, 0] + j] = GHOSTCHARACTER

                except IndexError:
                    pass
                    
        string = [f"█{' '.join(s)}▌" for s in string] 
        string = ["▄"*len(string[0])] + string + ["▀"*len(string[0])]

        # Add garbage indicator

        garbageCount = displayData.pendingGarbage
        garbageStr = ["▄"] + [GARBAGECHARACTER if row < garbageCount else " " for row in range(displayData.hiddenRows)][::-1] + ["▀"]
        rightBoundary = ["▄"] + ["▐" for i in range(displayData.hiddenRows)] + ["▀"]

        string = [row + garbageStr[i] + rightBoundary[i] for i, row in enumerate(string)]

        # Pad the grid, add Hold and Preview.

        N = MINPAD + EXTRAPAD # total characters

        padding = " "*N
        for i, line in enumerate(string):
            string[i] = padding + line + padding

        if len(string) < 8:
            for i in range (0, 8 - len(string)):
                string.append("\n")

        holdText = "Hold:"
        bagText = "Next:"
        string[UIVERTICALPAD] = string[UIVERTICALPAD][:N-len(holdText) - MINPAD] + holdText + string[UIVERTICALPAD][N - MINPAD:len(string[UIVERTICALPAD]) - N + MINPAD] + bagText + string[UIVERTICALPAD][len(string[UIVERTICALPAD]) - N + len(bagText) + MINPAD : len(string[UIVERTICALPAD])]

        if displayData.heldTetromino:

            # Can move this to function (albeit with quite a few params) for re-use below
            holdPieceMatrix = displayData.heldTetromino.matrix
            uiRow = UIVERTICALPAD + 1 + PIECEPAD
            for y in range(holdPieceMatrix.shape[1]):
                matrixRowStr = str(holdPieceMatrix[y])[1:-1].replace("0", " ")

                string[uiRow + y] = string[uiRow + y][:N-len(matrixRowStr) - MINPAD] + matrixRowStr + string[uiRow + y][N - MINPAD:]

        if displayData.combo > 0:
            if displayData.combo > 99: 
                comboStr = f" Combo! (x99+)"
            else:
                comboStr = f" Combo! (x{displayData.combo})"
                
            string[COMBOROW] = comboStr + string[COMBOROW][len(comboStr):]


        uiRow = UIVERTICALPAD + 1 + PIECEPAD
        
        for i in range(0, 5):
            
            piece = displayData.bag[i]
            pieceMatrix = piece.matrix
            pieceRows = pieceMatrix.shape[1]
            rowsSkipped = 0
            
            if uiRow + pieceRows > displayData.grid.shape[0]:
                break

            for y in range(pieceRows):
                if np.all(pieceMatrix[y] == 0):
                    rowsSkipped += 1
                else:
                    matrixRowStr = str(pieceMatrix[y])[1:-1].replace("0", " ")
                    drawRow = uiRow + y - rowsSkipped

                    string[drawRow] = string[drawRow][:len(string[drawRow]) - N + MINPAD] + matrixRowStr + string[drawRow][len(string[drawRow]) - N + len(matrixRowStr) + MINPAD : len(string[drawRow])]

            uiRow += pieceRows + PIECEPAD - rowsSkipped

        # Add current actions:

        actionStr = [
            f"\t\"{KeyIcons.entries[Action.RotateLeft]}\"\t\"{KeyIcons.entries[Action.RotateRight]}\"\t\"{KeyIcons.entries[Action.Rotate180]}\"\t\"{KeyIcons.entries[Action.Hold]}\"\t\"{KeyIcons.entries[Action.Left]}\"\t\t\"{KeyIcons.entries[Action.Right]}\"",
            f"\t\t\t\t\t\t\"{KeyIcons.entries[Action.SoftDrop]}\"\t",
            f"\t\t\t\t\"{KeyIcons.entries[Action.HardDrop]}\"\t\t\t"
        ]

        actionStr = "\n".join(actionStr)

        # Create a separate score string
        scoreToString = f"{displayData.score}pts"
        scorePadLength = max(0, int(len(string[-1]) // 2 - len(scoreToString) // 2))
        scoreString = " "*scorePadLength + scoreToString
        scoreString = scoreString + " "*(len(string[-1]) - len(scoreString))

        #DEBUG - REDUNDANT, REMOVE.

        if DEBUG:
            debugStr = "" #f"\n\nFrame: {self.__frame}ff \tTick: {self.__tick}fff\tDAS Charge: {self.DAScharge}fff\tARR Frame tick: {self.ARRframeTick}fff\tLock tick: {self.__lockTick}fff\nDrop Hover: {ghostPos}ffffff\tPiece Pos: {self.currentTetromino.pos}ffffff\tLast move was rotate: {self.currentTetromino.lastMoveWasRotate}fffff\nScore: {self.score}fffff"
        else:
            debugStr = ""

        # @Return Main grid string, score string, previous drop type for prompts.
        return "\n" + "\n".join(string), scoreString, displayData.lastDropType, actionStr, debugStr

    ########################################################################### Action Helper Funcs

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

    def __isActionToggled(self, action):
        return self.keyInfo[self.keybindings[action]]["cur"] and not self.keyInfo[self.keybindings[action]]["prev"]

    def __isActionDown(self, action):
        return self.keyInfo[self.keybindings[action]]["cur"]

    def __doActionCheck(self, action, checkFunc):

        if checkFunc(action):
            self.ac[action] = True
        else:
            self.ac[action] = False

    ########################################################################### Keypress Helper Funcs

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

if __name__ == "__main__":
    game = CmdInstance()
    game.run()