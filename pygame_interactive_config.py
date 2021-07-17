import pygame as pg
from util import Tetrominos, lerpBlendRGBA

class PygameInteractiveConfig:

    windowDimensions = (1920,1080)
    gameDimensions = (960, 1080)
    windowCaption = "Tensorflow Tetris"

    colorSwatch = ["0xBCEDF6", "0x6B7FD7", "0x320E3B", "0x4C2A85", "0xDDFBD2"]

    gridBackgroundColor = (0, 0, 0)
    gridBorderThickness = 3
    gridBorderColor = lerpBlendRGBA(gridBackgroundColor, (255,255,255), 0.7)
    gridDivisorWidth = 1 #px
    gridDivisorColor = lerpBlendRGBA(gridBackgroundColor, (255,255,255), 0.1)
    

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