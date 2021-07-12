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

    DAS = 2
    ARR = 1
    SDF = 60    # Ticks per frame while softdropping (normal drop = 1 tick/frame)

class GameConfig():

    useSevenBag = True

    frameRate = 120
    G = 20      #  Ticks per drop.
    lockDelay = 10
