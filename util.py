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