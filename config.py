from util import Action
from pynput import keyboard

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

class HandlingConfig():

    DAS = 1
    ARR = 1
    SDF = 5

class GameConfig():

    tickRate = 60
    frameRate = 120

    lockDelay = 1
    G = 20      #  Ticks per drop.