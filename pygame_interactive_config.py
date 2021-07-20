import pygame as pg
from util import Tetrominos, lerpBlendRGBA, Action, ScoreTypes

class PygameInteractiveConfig:

    windowDimensions = (960,1080)
    gameDimensions = (960, 1080)
    windowCaption = "Tensorflow Tetris"

    relativeFontPath = ("pygame_assets", "Raleway-bold.ttf")

    colorSwatch = ["0xBCEDF6", "0x6B7FD7", "0x320E3B", "0x4C2A85", "0xDDFBD2"]

    ghostAlpha = 0.3

    gridBackgroundColor = (0, 0, 0)
    gridBorderThickness = 3
    gridBorderColor = lerpBlendRGBA(gridBackgroundColor, (255,255,255), 0.7)
    gridDivisorWidth = 1 #px
    gridDivisorColor = lerpBlendRGBA(gridBackgroundColor, (255,255,255), 0.1)

    garbageIndicatorColor = pg.Color('red')
    garbageIndicatorWarningColor = pg.Color('yellow')
    
    colorTable = {
        Tetrominos.I.value + 1: "0x73BEEA",
        Tetrominos.J.value + 1: "0x8194FF",
        Tetrominos.L.value + 1: "0xFFCB90",
        Tetrominos.S.value + 1: "0x91D9A7",
        Tetrominos.Z.value + 1: "0xEA6989",
        Tetrominos.T.value + 1: "0xE586FA",
        Tetrominos.O.value + 1: "0xFFF878",
    }

    garbageColor = "0xE0E2Ef"

    keybindings = {
        Action.Left:            pg.K_LEFT,
        Action.Right:           pg.K_RIGHT,
        Action.SoftDrop:        pg.K_DOWN,
        Action.HardDrop:        pg.K_SPACE,
        Action.RotateLeft:      pg.K_UP,
        Action.RotateRight:     pg.K_z,
        Action.Rotate180:       pg.K_x,
        Action.Hold:            pg.K_c
    }

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