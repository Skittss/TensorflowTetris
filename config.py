from util import Action, ScoreTypes
from pynput import keyboard
from colorama import Fore, Back, Style
import numpy as np

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

class HandlingConfig():

    DAS = 1
    ARR = 1
    SDF = 60    # Ticks per frame while softdropping (normal drop = 1 tick/frame)

class GameConfig():

    useSevenBag = True

    frameRate = 120
    G = 20      #  Ticks per drop.
    lockDelay = 10

    garbageInitialDelay = 60 #frameRate * 3    # No of frames.
    garbageRepeatDelay = 20

    I_kicks = {
            "01": np.array([[0,0], [-2,0], [1, 0], [-2, 1], [ 1,-2]]),
            "10": np.array([[0,0], [2, 0], [-1,0], [ 2,-1], [-1, 2]]),
            "12": np.array([[0,0], [-1,0], [2 ,0], [-1,-2], [ 2, 1]]),
            "21": np.array([[0,0], [1, 0], [-2,0], [ 1, 2], [-2,-1]]),
            "23": np.array([[0,0], [2, 0], [-1,0], [ 2,-1], [-1, 2]]),
            "32": np.array([[0,0], [-2,0], [1, 0], [-2, 1], [ 1,-2]]),
            "30": np.array([[0,0], [1, 0], [-2,0], [ 1, 2], [-2,-1]]),
            "03": np.array([[0,0], [-1,0], [2, 0], [-1,-2], [ 2, 1]]),

            "02": np.array([[0,0], [-1, 0], [-2, 0], [ 1, 0], [ 2, 0]]),
            "20": np.array([[0,0], [ 0, 1], [ 0,-1], [ 0,-2], [ 0, 2]]),
            "13": np.array([[0,0], [ 1, 0], [ 2, 0], [-1, 0], [-2, 0]]),
            "31": np.array([[0,0], [ 0, 1], [ 0,-1], [ 0,-2], [ 0, 2]])
    }

    O_kicks = np.array([[0,0]])

    Other_kicks = {
            "01": np.array([[0,0], [-1,0], [-1,-1], [0, 2], [-1, 2]]),
            "10": np.array([[0,0], [1, 0], [ 1, 1], [0,-2], [ 1,-2]]),
            "12": np.array([[0,0], [1, 0], [ 1, 1], [0,-2], [ 1,-2]]),
            "21": np.array([[0,0], [-1,0], [-1,-1], [0, 2], [-1, 2]]),
            "23": np.array([[0,0], [1, 0], [ 1,-1], [0, 2], [ 1, 2]]),
            "32": np.array([[0,0], [-1,0], [-1, 1], [0,-2], [-1,-2]]),
            "30": np.array([[0,0], [-1,0], [-1, 1], [0,-2], [-1,-2]]),
            "03": np.array([[0,0], [1, 0], [ 1,-1], [0, 2], [ 1, 2]]),

            "02": np.array([[0,0], [ 0,-1], [ 1,-1], [-1,-1], [ 1, 0], [-1, 0]]),
            "20": np.array([[0,0], [ 0, 1], [-1, 1], [ 1, 1], [-1, 0], [ 1, 0]]),
            "13": np.array([[0,0], [ 1, 0], [ 1,-2], [ 1,-1], [ 0,-2], [ 0,-1]]),
            "31": np.array([[0,0], [-1, 0], [-1,-2], [-1,-1], [ 0,-2], [ 0,-1]]),
    }

    scoreTable = {
        ScoreTypes.Drop: 10,
        ScoreTypes.HardDrop: 20,
        ScoreTypes.Single: 100,
        ScoreTypes.Double: 200,
        ScoreTypes.Triple: 500,
        ScoreTypes.Tetris: 800,
        ScoreTypes.MiniTSpin: 100,
        ScoreTypes.TSpin: 400,
        ScoreTypes.MiniTSpinSingle: 200,
        ScoreTypes.MiniTSpinDouble: 400,
        ScoreTypes.TSpinSingle: 800,
        ScoreTypes.TSpinDouble: 1200,
        ScoreTypes.TSpinTriple: 1600,
        ScoreTypes.SinglePC: 800,
        ScoreTypes.DoublePC: 1200,
        ScoreTypes.TriplePC: 1800,
        ScoreTypes.TetrisPC: 2000
    }
