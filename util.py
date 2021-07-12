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