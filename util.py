from enum import Enum

class Action(Enum):
    Left = 0
    Right = 1
    SoftDrop = 2
    HardDrop = 3
    RotateLeft = 4
    RotateRight = 5
    Rotate180 = 6
    Hold = 7

class KeyIcons:

    entries = {
        Action.Left: "<-",
        Action.Right: "->",
        Action.SoftDrop: "\/",
        Action.HardDrop: "H DROP",
        Action.RotateLeft: "CCW",
        Action.RotateRight: "CW",
        Action.Rotate180: "FLIP",
        Action.Hold: "HOLD"
    }

class ScoreTypes(Enum):
    Drop = 0
    HardDrop = 1
    Single = 2
    Double = 3
    Triple = 4
    Tetris = 5
    MiniTSpin = 6
    TSpin = 7
    MiniTSpinSingle = 8
    MiniTSpinDouble = 9
    TSpinSingle = 10
    TSpinDouble = 11
    TSpinTriple = 12
