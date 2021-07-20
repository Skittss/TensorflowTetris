from util import Action, ScoreTypes
from pynput import keyboard
from colorama import Fore, Back, Style

class CmdInteractiveConfig():

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
        "0": Fore.BLACK,
        "1": Fore.LIGHTCYAN_EX,
        "2": Fore.LIGHTBLUE_EX,
        "3": Style.BRIGHT + Fore.YELLOW,
        "4": Fore.LIGHTYELLOW_EX,
        "5": Fore.LIGHTGREEN_EX,
        "6": Fore.LIGHTMAGENTA_EX,
        "7": Fore.LIGHTRED_EX,
        "#": Fore.RED
    }

    ghostPieceStyle = Style.BRIGHT + Fore.WHITE
    ghostCharacter = "@"
    actionHighlightStyle = Fore.LIGHTRED_EX

    promptTable = {
        ScoreTypes.Single: "Single",
        ScoreTypes.Double: "Double",
        ScoreTypes.Triple: "Triple",
        ScoreTypes.Tetris: "Tetris!",
        ScoreTypes.MiniTSpin: "T-Spin Mini",
        ScoreTypes.TSpin: "T-Spin",
        ScoreTypes.MiniTSpinSingle: "T-Spin Mini x1",
        ScoreTypes.MiniTSpinDouble: "T-Spin Mini x2",
        ScoreTypes.TSpinSingle: "T-Spin x1",
        ScoreTypes.TSpinDouble: "T-Spin x2",
        ScoreTypes.TSpinTriple: "T-Spin x3",
        ScoreTypes.SinglePC: "Perfect Clear! x1",
        ScoreTypes.DoublePC: "Perfect Clear! x2",
        ScoreTypes.TriplePC: "Perfect Clear! x3",
        ScoreTypes.TetrisPC: "Perfect Clear! x4"
    }