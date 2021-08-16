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
    RotateLeft = 2
    RotateRight = 3
    Rotate180 = 4
    SoftDrop = 5
    HardDrop = 6
    Hold = 7

def getEmptyActionObj():
    return {
        Action.Left: False,
        Action.Right: False,
        Action.RotateLeft: False,
        Action.RotateRight: False,
        Action.Rotate180: False,
        Action.SoftDrop: False,
        Action.HardDrop: False,
        Action.Hold: False
    }

def actionObjToStr(obj):
    str = "Action: "
    addStr = ""
    if obj[Action.Left]:
        addStr += "L "
    if obj[Action.Right]:
        addStr += "R "
    if obj[Action.RotateLeft]:
        addStr += "Rot-L "
    if obj[Action.RotateRight]:
        addStr += "Rot-R "
    if obj[Action.Rotate180]:
        addStr += "Rot-F "
    if obj[Action.SoftDrop]:
        addStr += "SoftDrop "
    if obj[Action.HardDrop]:
        addStr += "HardDrop "
    if obj[Action.Hold]:
        addStr+= "Hold "
    if len(addStr) == 0:
        addStr = "None"

    return str + addStr

def numpyCoordToTuple(coord):
    return (coord[0, 0], coord[0, 1])

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