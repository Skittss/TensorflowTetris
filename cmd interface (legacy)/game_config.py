from util import ScoreTypes
import numpy as np

class HandlingConfig():

    DAS = 1
    ARR = 1
    SDF = 60    # Ticks per frame while softdropping (normal drop = 1 tick/frame)

class GameConfig():

    seed = 11111
    garbageSeed = seed

    useSevenBag = True

    preview = 5

    frameRate = 60
    G = 20      #  Ticks per drop.
    lockDelay = 10
    comboTimer = 60

    garbageInitialDelay = 60 # No. of frames.
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

    attackTable = {
        ScoreTypes.Drop: 0,
        ScoreTypes.HardDrop: 0,
        ScoreTypes.Single: 0,
        ScoreTypes.Double: 1,
        ScoreTypes.Triple: 2,
        ScoreTypes.Tetris: 4,
        ScoreTypes.MiniTSpin: 0,
        ScoreTypes.TSpin: 0,
        ScoreTypes.MiniTSpinSingle: 1,
        ScoreTypes.MiniTSpinDouble: 2,
        ScoreTypes.TSpinSingle: 2,
        ScoreTypes.TSpinDouble: 4,
        ScoreTypes.TSpinTriple: 6,
        ScoreTypes.SinglePC: 10,
        ScoreTypes.DoublePC: 10,
        ScoreTypes.TriplePC: 10,
        ScoreTypes.TetrisPC: 10
    }

    comboTable = lambda x: 1 if x > 1 else 0
