from enum import Enum
from math import ceil

# Why does pygame not do per-surface blending???
def lerpBlendRGBA(base, overlay, alpha):

    r1, g1, b1 = base
    r2, g2, b2 = overlay

    blend = lambda b, o: alpha * o + (1 - alpha) * b

    return (blend(r1, r2), blend(g1, g2), blend(b1, b2))

def hexstrToRGB(col):
    col=col[2:]
    return tuple(int(col[i:i+2], 16) for i in (0, 2, 4))

def msToFrames(framerate, ms):
    return ceil((ms / 1000) * framerate)

class Action(Enum):
    Left = 0
    Right = 1
    SoftDrop = 2
    HardDrop = 3
    RotateLeft = 4
    RotateRight = 5
    Rotate180 = 6
    Hold = 7

def getEmptyActionObj():
    return {
        Action.Left: False,
        Action.Right: False,
        Action.SoftDrop: False,
        Action.HardDrop: False,
        Action.RotateLeft: False,
        Action.RotateRight: False,
        Action.Rotate180: False,
        Action.Hold: False
    }

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
    SinglePC = 13
    DoublePC = 14
    TriplePC = 15
    TetrisPC = 16

class Tetrominos(Enum):
    I = 0
    J = 1
    L = 2
    O = 3
    S = 4
    T = 5
    Z = 6