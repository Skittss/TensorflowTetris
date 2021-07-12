from util import Action
from pynput import keyboard
from colorama import Fore, Style

class InteractiveConfig():

    keybindings = {
        Action.Left:            keyboard.Key.left,
        Action.Right:           keyboard.Key.right,
        Action.SoftDrop:        keyboard.Key.down,
        Action.HardDrop:        keyboard.Key.space,
        Action.RotateLeft:      keyboard.Key.up,
        Action.RotateRight:     'z',
        Action.Rotate180:       'x',
        Action.Hold:            'c'
    }

    pieceStyles = {
        "0": Fore.WHITE,
        "1": Fore.CYAN,
        "2": Fore.BLUE,
        "3": Fore.YELLOW,
        "4": Fore.LIGHTYELLOW_EX,
        "5": Fore.GREEN,
        "6": Fore.MAGENTA,
        "7": Fore.RED
    }

    ghostPieceStyle = Style.BRIGHT + Fore.CYAN
    ghostCharacter = "@"

class HandlingConfig():

    DAS = 2
    ARR = 1
    SDF = 60    # Ticks per frame while softdropping (normal drop = 1 tick/frame)

class GameConfig():

    useSevenBag = True

    frameRate = 120
    G = 20      #  Ticks per drop.
    lockDelay = 10
