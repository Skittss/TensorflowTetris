import numpy as np
import math
from util import Action, ScoreTypes, Tetrominos
from collections import deque
from secrets import randbelow

# TODO      
#           ---Modify piece spawn positions to be correctly centered.
#           ---Point System
#           ---Show points from line clears above/below points
#           ---DAS, 
#           ---ARR,
#           ---SDF
#           ---Lock delay
#           ---Gravity - G, If moved more than one downwards in a single frame, re-do input? Maybe not for now.
#           ---Check spawn orientations. Reset orientation on hold.
#           ---Fix wall kicks.
#           ---Current actions displayed on __str__
#           ---Hidden rows
#           ---Add line clear type to __str__ i.e. tetris / t-spin mini etc.
#           ---Garbage meter with red # added to __str__
#           ---Ghost piece added to __str__
#           Sometimes kick not working on right wall - fix.
#           ---Fix top out when piece falls as garbage rises, I think the piece can't push to the garbage?
#           --- -ve indexing causes by topout. immediately harddrop all pieces to replicate.

class TetrisGameState:

    def __init__(self):

        self.lastDropClass = None
        self.currentReward = None
        self.pieceCount = None

        self.score = None
        self.lost = None

        self.grid = None

        self.tick = None
        self.frame = None
        self.lockTick = None

        self.comboCounterState = None

        self.DAScharge = None
        self.ARRframeTick = None

        self.currentTetrominoState = None
        self.heldTetrominoState = None
        self.heldLastPiece = None

        self.bagRandomState = None
        self.bagState = None

        self.garbageRandomState = None
        self.garbageState = None

class Tetris:

    class Tetromino:

        @classmethod
        def fromState(cls, state):
            return cls(None, None, None, state=state)

        def __init__(self, matrices, startPos, tag = 0, centreStartPos = True, state=None):

            if state:
                self.loadState(state)

            else:

                self.tag = tag
                self.matrix = matrices[tag]

                if centreStartPos:
                    self.startPos = startPos -  np.array([[int(math.floor(self.matrix.shape[1] / 2)), 0]])
                else :
                    self.startPos = startPos

                self.pos = self.startPos
                self.rotateState = 0
                self.lastMoveWasRotate = False
                self.wasKicked1x2 = False

        def resetPos(self):
            
            self.pos = self.startPos

        def rotate(self, k = 1):

            self.matrix = np.rot90(self.matrix, k)
            self.rotateState = (self.rotateState - k) % 4

        def getRotatedMatrix(self, k = 1):

            mat = np.rot90(self.matrix, k)
            nextRotateState = (self.rotateState - k) % 4
            return nextRotateState, mat

        def translate(self, vector):
            self.pos = np.add(self.pos, vector)

        def resetMatrix(self, matrices):
            self.matrix = matrices[self.tag]

        def loadState(self, state):
            self.tag, mat, startPos, pos, self.rotateState, self.lastMoveWasRotate, self.wasKicked1x2 = state
            self.matrix = mat.copy()
            self.startPos = startPos.copy()
            self.pos = pos.copy()

        def saveState(self):
            return (self.tag, self.matrix.copy(), self.startPos.copy(), self.pos.copy(), self.rotateState, self.lastMoveWasRotate, self.wasKicked1x2)

        def __str__(self):

            return f"<Tetromino: {self.tag}-piece>"

    class GarbageList:

        def __init__(self, INITIAL_DELAY, REPEAT_DELAY, MAX_GARBAGE):

            self.maxGarbage = MAX_GARBAGE
            self.garbage = []
            self.delay = INITIAL_DELAY
            self.repeatDelay = REPEAT_DELAY

        def add(self, n):
            for i in range(0, n):
                if len(self.garbage < self.maxGarbage):
                    self.garbage.append(self.delay + (i * self.repeatDelay))

            self.garbage.sort(reverse=True)

        def tick(self):
            count = 0
            for g in range(0, len(self.garbage)):
                self.garbage[g] -= 1
                if self.garbage[g] <= 0:
                    count += 1

            self.garbage = [x for x in self.garbage if x > 0]

            return count

        def pending(self):
            return len(self.garbage)
        
        def pendingNextTick(self):

            if len(self.garbage) == 0:
                return [0, 0]
            
            closestTick = 0
            for i in range(1, len(self.garbage)):
                if self.garbage[i] < self.garbage[closestTick]:
                    closestTick = i

                elif self.garbage[i] > self.garbage[closestTick]:
                    break

            # @Returns amt, tick
            return [i, self.garbage[closestTick]]

        def counter(self, n):
            remaining = len(self.garbage) - n
            if remaining <= 0:
                self.garbage = []
            else:
                self.garbage = self.garbage[remaining - 1:]

            # @Returns number of lines to be sent after countering.
            return max(0, n - len(self.garbage))

        def loadState(self, state):
            self.garbage = state.copy()

        def saveState(self):
            return self.garbage.copy()

    class Combo:

        def __init__(self, TIMER, COMBOFUNC):

            self.__comboPieces = 0
            self.__table = COMBOFUNC
            self.__timer = TIMER
            self.__tick = 0

        def getCombo(self):
            return max(0, self.__comboPieces - 1)

        def getNormTimeRemaining(self):
            return self.__tick / self.__timer

        def tick(self):
            if self.__tick > 0:
                self.__tick -= 1
            
            if self.__tick == 0:
                self.__comboPieces = 0

        def add(self, dropClass):

            if not (dropClass == ScoreTypes.Drop or dropClass == ScoreTypes.HardDrop):

                self.__comboPieces += 1
                self.__tick = self.__timer

                return self.__table(self.getCombo())
                
            return 0

        def loadState(self, state):
            self.__comboPieces, self.__tick = state
        
        def saveState(self):
            return (self.__comboPieces, self.__tick)

    class DisplayData:

        def __init__(self,
            grid=None,
            hiddenRows=None,

            ghostPos=None,

            pendingGarbage=None,
            garbageValue=None,

            score=None,
            lost=None,

            bag=None,
            preview=None,
            currentTetrominoMatrix=None,
            heldTetromino=None,

            combo=None,
            lastDropType=None,
        ):
            self.grid = grid
            self.hiddenRows = hiddenRows
            self.ghostPos = ghostPos
            self.pendingGarbage = pendingGarbage
            self.garbageValue = garbageValue
            self.score = score
            self.lost = lost
            self.bag = bag
            self.preview = preview
            self.currentTetrominoMatrix = currentTetrominoMatrix
            self.heldTetromino = heldTetromino
            self.combo = combo
            self.lastDropType = lastDropType
            
    def __init__(self, gameConfig, handlingConfig, cols = 10, rows = 20, bagSize = 2, seed = None, garbageSeed = None):

        self.__lastDropClass = None
        self.currentReward = 0
        self.pieceCount = 0

        # Pts & Game over
        self.score = 0
        self.scoreTable = gameConfig.scoreTable
        self.__lost = False

        # Grid information 
        self.cols = cols
        self.rows = rows * 2
        self.hiddenRows = rows
        self.grid = np.zeros([self.rows, self.cols])

        # Framerate related info
        self.__tick = 0
        self.__frame = 0
        self.__G = gameConfig.G
        self.__frameRate = gameConfig.frameRate
        self.__lockDelay = gameConfig.lockDelay
        self.__lockTick = 0

        # Combos
        self.comboCounter = self.Combo(gameConfig.comboTimer, gameConfig.comboTable)

        # DAS, ARR, SDF
        self.DAS = handlingConfig.DAS
        self.DAScharge = 0

        self.ARR = handlingConfig.ARR
        self.ARRframeTick = 0

        self.SDF = handlingConfig.SDF

        # Hold & Current piece
        self.currentTetromino = None
        self.heldTetromino = None
        self.heldLastPiece = False

        # Tetromino mapping to matrices
        self.tetrominoMatrices = self.__getTetrominoMatrices()
        self.tetrominoStartPos = np.array([[math.floor(self.cols / 2), self.hiddenRows - 1]])

        # Bag
        self.seed = seed if seed else randbelow(30000)

        self.bagRandom = np.random.default_rng(seed = seed)
        self.bag = self.__getBag(bagSize)
        self.preview = gameConfig.preview

        # Garbage

        self.garbageSeed = garbageSeed if garbageSeed else randbelow(30000)

        self.garbageRandom = np.random.default_rng(seed = garbageSeed)
        self.garbageValue = 9
        self.garbage = self.GarbageList(gameConfig.garbageInitialDelay, gameConfig.garbageRepeatDelay, self.rows * 2)
        self.attackTable = gameConfig.attackTable

        # Wall kick tests - Could reduce hashmaps by noting "xy" == -"yx", but keep things simple for now.
        self.__wallKickTestsI = gameConfig.I_kicks

        self.__wallKickTestsO = gameConfig.O_kicks

        self.__wallKickTestsOther = gameConfig.Other_kicks

        self.__getNextTetromino()

        test = self.saveState()

        self.loadState(test)

        #self.receiveGarbage(20)

    def getState(self, SOLO_AGENT = True):
        # Return a flattened array with information from:
        #   binary board values (0=empty, 1=filled) including hidden rows. This assumes the agent has perfect memory.
        #   piece previews - one hot encoding.      --->    Moved to agent to avoid importing TF here.
        #   current piece position
        #   current piece rotation
        #   DAS charge tick - normalized to [-1, 1]
        #   ARR tick - normalized to [0, 1]
        #   Lock delay tick - normalized to [0, 1]
        #   combo - binary, 0 for no combo, 1 for current combo as higher combos do not yield higher rewards.
        #   combo timer - nomalized to [0, 1]
        #   pending garbage                                     ----|
        #   next pending garbage amount                             |--- Do not apply to Solo Agent.
        #   next pending garbage timer                          ----|

        grid = self.grid.flatten().tolist()
        
        extra =  self.currentTetromino.pos.flatten().tolist() + \
            [self.currentTetromino.rotateState, self.__getNormDAScharge(), self.__getNormARRtick(), self.__getNormLockTick(), self.__hasOngoingCombo(), self.comboCounter.getNormTimeRemaining()]

        if not SOLO_AGENT:
            extra += [self.garbage.pending()] + self.garbage.pendingNextTick()

        return grid, extra

    def getBagPreview(self):
        return [self.bag[i].tag for i in range(self.preview)]

    def __hasOngoingCombo(self):
        return 1 if self.comboCounter.getCombo() > 0 else 0

    def __getNormDAScharge(self):
        return self.DAScharge / self.DAS

    def __getNormARRtick(self):
        return self.ARRframeTick / self.ARR

    def __getNormLockTick(self):
        return self.__lockTick / self.__lockDelay

    def getSeeds(self):
        return self.seed, self.garbageSeed

    def getDisplayData(self):

        return self.DisplayData(
            grid=self.grid,
            hiddenRows=self.hiddenRows,
            ghostPos = self.__findCurrentHarddropPosition() - np.array([[0, self.hiddenRows]]),
            pendingGarbage = self.garbage.pending(),
            garbageValue= self.garbageValue,
            score = self.score,
            lost = self.__lost,
            bag = self.bag,
            preview = self.preview,
            currentTetrominoMatrix = self.currentTetromino.matrix,
            heldTetromino = self.heldTetromino,
            combo = self.comboCounter.getCombo(),
            lastDropType = self.__lastDropClass
        )

    def nextState(self, actions, garbageTarget=None):

        if not self.__lost:

            self.currentReward = 0

            self.__doDASandARRreset(actions)

            self.__popCurrentTetrominoFromGrid()

            # Perhaps needs to be moved to after action is done.
            linesToAdd = self.garbage.tick()

            self.comboCounter.tick()

            if linesToAdd > 0:
                self.__lost = self.__addGarbageLines(linesToAdd)

            # Adding garbage may cause top-out
            if not self.__lost:

                downwardMoveCount = self.__updateTick(actions)

                self.__doActions(actions)

                pieceDropped = self.__attemptDownwardMoves(downwardMoveCount)

                self.__pushCurrentTetrominoToGrid()

                if pieceDropped:

                    self.pieceCount += 1

                    self.__lockTick = 0

                    self.heldLastPiece = False

                    # Don't actually clear lines the first time around else it messes up the classification
                    linesCleared = self.__clearLines(clear = False)

                    self.__lastDropClass = self.__classifyDrop(linesCleared)

                    scoreIncrease = self.scoreTable[self.__lastDropClass]

                    self.currentReward += scoreIncrease
                    self.score += scoreIncrease

                    self.__clearLines()

                    comboLines = self.comboCounter.add(self.__lastDropClass)

                    if garbageTarget:
                        
                        toSend = self.__getBaseLinesToSend(self.__lastDropClass) + comboLines
                        self.sendGarbage(toSend, garbageTarget)

                    self.__lost = not self.__getNextTetromino()

                self.__frame = (self.__frame + 1) % self.__frameRate

                return True, (self.currentReward, self.pieceCount)

            else:
                self.__pushCurrentTetrominoToGrid()

                self.__frame = (self.__frame + 1) % self.__frameRate

                return False, (0, self.pieceCount)

        else:
            return False, (0, self.pieceCount)

    def receiveGarbage(self, n):
        self.garbage.add(n)

    def sendGarbage(self, n, receiveFunc):
        toSend = self.garbage.counter(n)
        receiveFunc(toSend)

    def __withinGrid(self, pos):
        return 0 < pos[0, 0] < self.cols and 0 < pos[0, 1] < self.rows

    def __isOccupied(self, pos):
        if not self.__withinGrid(pos):
            return True

        return self.grid[self.currentTetromino.pos[0, 1], self.currentTetromino.pos[0, 0]] > 0

    def __getTbackAndFrontOffsets(self):
        # @Return back1, back2, front1, front2

        if self.currentTetromino.rotateState == 0:
            return np.array([[0, 2]]), np.array([[2, 2]]), np.array([[0, 0]]), np.array([[2, 0]])

        if self.currentTetromino.rotateState == 1:
            return np.array([[0, 0]]), np.array([[0, 2]]), np.array([[2, 0]]), np.array([[2, 2]])

        if self.currentTetromino.rotateState == 2:
            return np.array([[0, 0]]), np.array([[2, 0]]), np.array([[0, 2]]), np.array([[2, 2]])
        
        else:
            return np.array([[2, 0]]), np.array([[2, 2]]), np.array([[0, 0]]), np.array([[0, 2]])



    def __threeCornerCheck(self):

        backCornerCount = 0
        frontCornerCount = 0

        b_o1, b_o2, f_o1, f_o2 = self.__getTbackAndFrontOffsets()

        if self.__isOccupied(self.currentTetromino.pos + b_o1):
            backCornerCount += 1

        if self.__isOccupied(self.currentTetromino.pos + b_o2):
            backCornerCount += 1

        if self.__isOccupied(self.currentTetromino.pos + f_o1):
            frontCornerCount += 1

        if self.__isOccupied(self.currentTetromino.pos + f_o2):
            frontCornerCount += 1

        if backCornerCount > 0 and frontCornerCount == 2:
            return 1
        elif frontCornerCount == 1 and backCornerCount == 2:
            if self.currentTetromino.wasKicked1x2:
                return 1
            else:
                return 0

        return -1


    def __didCurrentPieceTspin(self):
        # @return -1: No, 0: T-Spin mini, 1: T-spin (full)
        if self.currentTetromino.tag == Tetrominos.T.value and self.currentTetromino.lastMoveWasRotate:
            return self.__threeCornerCheck()
        else:
            return -1

    def __isPC(self):
        return not self.grid.any()

    def __getBaseLinesToSend(self, dropClass):
        return self.attackTable[dropClass]

    def __classifyDrop(self, linesCleared):

        if linesCleared == 0:
            base = ScoreTypes.Drop
        elif linesCleared == 1:
            base = ScoreTypes.Single
        elif linesCleared == 2:
            base = ScoreTypes.Double
        elif linesCleared == 3:
            base = ScoreTypes.Triple
        else:
            base = ScoreTypes.Tetris

        if self.__isPC():

            if base == ScoreTypes.Single:
                return ScoreTypes.SinglePC

            if base == ScoreTypes.Double:
                return ScoreTypes.DoublePC

            if base == ScoreTypes.Triple:
                return ScoreTypes.TriplePC

            if base == ScoreTypes.Tetris:
                return ScoreTypes.TetrisPC


        if base == ScoreTypes.Tetris:
            return base

        tspinModifier = self.__didCurrentPieceTspin()

        if tspinModifier < 0:
            return base

        if tspinModifier == 0:

            if base == ScoreTypes.Drop:
                return ScoreTypes.MiniTSpin

            if base == ScoreTypes.Single:
                return ScoreTypes.MiniTSpinSingle

            if base == ScoreTypes.Double:
                return ScoreTypes.MiniTSpinDouble

        if tspinModifier == 1:
            
            if base == ScoreTypes.Drop:
                return ScoreTypes.TSpin

            if base == ScoreTypes.Single:
                return ScoreTypes.TSpinSingle

            if base == ScoreTypes.Double:
                return ScoreTypes.TSpinDouble

            if base == ScoreTypes.Triple:
                return ScoreTypes.TSpinTriple

        return ScoreTypes.Drop
    
    def __updateTick(self, actions):
        # Update the substep; If hard-drop, go to next full step, If soft drop, increment multiple times

        if actions[Action.HardDrop]:
            self.__tick = 0
            return -1

        if actions[Action.SoftDrop]:
            downMoves, self.__tick = divmod(self.__tick + self.SDF, self.__G)
            return downMoves

        downMoves, self.__tick = divmod(self.__tick + 1, self.__G)
        return downMoves

    def __doActions(self, actions):

        # didLRmove = False

        for a in actions:

            if actions[a]:
                
                if a == Action.Hold:
                    self.__hold()
                    
                elif a == Action.Left:
                    self.__moveLeft()
                    
                elif a == Action.Right:
                    self.__moveRight()
                    
                elif a == Action.RotateLeft:
                    self.__rotateLeft()
                    
                elif a == Action.RotateRight:
                    self.__rotateRight()
                    
                elif a == Action.Rotate180:
                    self.__rotate180()

    def __doDASandARRreset(self, actions):
        if not actions[Action.Left] and not actions[Action.Right]:
            self.DAScharge = 0
            self.ARRframeTick = 0
            return

        if self.DAScharge > 0 and actions[Action.Left] and not actions[Action.Right]:
            self.DAScharge = 0
            self.ARRframeTick = 0
            return

        if self.DAScharge < 0 and not actions[Action.Left] and actions[Action.Right]:
            self.DAScharge = 0
            self.ARRframeTick = 0
            return

    def __updateDASandARR(self, dasIncrement):
        
        newCharge = self.DAScharge + dasIncrement

        if -self.DAS <= newCharge <= self.DAS:
            self.DAScharge = newCharge
        else:
            self.__incrementARRtick()

    def __incrementARRtick(self):
        if self.ARR > 0:
            self.ARRframeTick = (self.ARRframeTick + 1) % self.ARR

    def __canMoveOnCurrentFrame(self, dir=-1):

        return self.DAScharge == 0 or (dir * self.DAScharge == self.DAS and (self.ARRframeTick == self.ARR - 1 or self.ARR == 0))

    def __doMove(self, translation):
        canMove = self.canPlaceOnGrid(self.currentTetromino.matrix, self.currentTetromino.pos + np.array([translation]))

        if canMove:
            self.currentTetromino.translate(np.array([translation]))

        return canMove

    def __moveLeft(self):

        self.currentTetromino.lastMoveWasRotate = False

        if self.__canMoveOnCurrentFrame():

            canMove = self.__doMove([-1, 0])

            # Move left until not possible any more
            if self.ARR == 0 and abs(self.DAScharge) == self.DAS:
                while canMove:
                    canMove = self.__doMove([-1, 0])
                
        self.__updateDASandARR(-1)

    def __moveRight(self):

        self.currentTetromino.lastMoveWasRotate = False

        if self.__canMoveOnCurrentFrame(dir=1):

            canMove = self.__doMove([1, 0])

            if self.ARR == 0 and abs(self.DAScharge) == self.DAS:
                while canMove:
                    canMove = self.__doMove([1, 0])

        self.__updateDASandARR(1)

    def __rotateLeft(self):
        self.__doRotation(1)

    def __rotateRight(self):
        self.__doRotation(3)

    def __rotate180(self):
        self.__doRotation(2)

    def __doRotation(self, k):

        translation = self.__canRotate(k)

        if not type(translation) == type(None):
            self.currentTetromino.lastMoveWasRotate = True
            self.currentTetromino.rotate(k)
            self.currentTetromino.translate(translation)

    def __canRotate(self, k):

        nextRotateState, rotatedMatrix = self.currentTetromino.getRotatedMatrix(k)

        for i, testTranslation in enumerate(self.__getWallKickTests(nextRotateState)):
            if self.canPlaceOnGrid(rotatedMatrix, self.currentTetromino.pos + testTranslation):

                if i == 4:
                    self.currentTetromino.wasKicked1x2 = True
                else:
                    self.currentTetromino.wasKicked1x2 = False

                return testTranslation

        return None

    def __getWallKickTests(self, nextRotateState):
        # Get wall kick tests for current tetromino

        if self.currentTetromino.tag == Tetrominos.O.value:
            return self.__wallKickTestsO

        if self.currentTetromino.tag == Tetrominos.I.value:
            tests = self.__wallKickTestsI
        else:
            tests = self.__wallKickTestsOther
        
        return tests[str(self.currentTetromino.rotateState) + str(nextRotateState)]

    def canPlaceOnGrid(self, matrix, pos):

        for x in range(0, matrix.shape[0]):
            for y in range(0, matrix.shape[1]):

                if not matrix[y, x] == 0:

                    checkPos = pos + np.array([[x, y]])

                    if checkPos[0, 0] < 0:
                        return False

                    if checkPos[0, 0] >= self.cols:
                        return False

                    if checkPos[0, 1] < 0:
                        return False

                    if checkPos[0, 1] >= self.rows:
                        return False

                    checkTileAgainst = self.grid[checkPos[0, 1], checkPos[0, 0]]
                    if not checkTileAgainst == 0:
                        return False

        return True

    def __hold(self):

        if not self.heldLastPiece:

            # Rest lock delay
            self.__lockTick = 0

            # Reset pos of current piece
            self.currentTetromino.resetPos()

            # Reset orientation of current piece
            self.currentTetromino.resetMatrix(self.tetrominoMatrices)

            # Swap hold piece if exists
            if self.heldTetromino:
                tmp = self.currentTetromino
                self.currentTetromino = self.heldTetromino
                self.heldTetromino = tmp

            else:
                self.heldTetromino = self.currentTetromino
                self.currentTetromino = self.__rotateBag()

            self.heldLastPiece = True

    def __findCurrentHarddropPosition(self):

        self.__popCurrentTetrominoFromGrid()

        downMoves = 0
        canMoveDown = True

        while canMoveDown:
            canMoveDown = self.canPlaceOnGrid(self.currentTetromino.matrix, self.currentTetromino.pos + np.array([[0, downMoves]]))

            if canMoveDown:
                downMoves += 1

        self.__pushCurrentTetrominoToGrid()

        return self.currentTetromino.pos + np.array([[0, downMoves - 1]])

    def __attemptDownwardMoves(self, count):
        
        canMoveDown = self.canPlaceOnGrid(self.currentTetromino.matrix, self.currentTetromino.pos + np.array([[0, 1]]))
                
        if canMoveDown:
            
            if (not count == 0):
                self.currentTetromino.lastMoveWasRotate = False
                self.currentTetromino.translate(np.array([[0, 1]]))

            if (count > 1):
                dropped = self.__attemptDownwardMoves(count - 1)
                return dropped

            elif (count < 0):
                dropped = self.__attemptDownwardMoves(count)
                return dropped

        else:
            if self.__lockTick < self.__lockDelay and not count < 0:
                self.__lockTick += 1
                canMoveDown = True
        
        return not canMoveDown

    def __getNextTetromino(self):
        self.currentTetromino = self.__rotateBag()
        return self.__pushCurrentTetrominoToGrid()
        
    def __popCurrentTetrominoFromGrid(self):
        
        gsv, gsh, tsv, tsh = self.__getSlicesFromGridOverlap()

        self.grid[gsv, gsh] -= self.currentTetromino.matrix[tsv, tsh]

    def __pushCurrentTetrominoToGrid(self, doPush=True):

        gsv, gsh, tsv, tsh = self.__getSlicesFromGridOverlap()

        canPush = True

        for g, t in zip(self.grid[gsv, gsh], self.currentTetromino.matrix[tsv, tsh]):
            for g_v, t_v in zip(g, t):
                if not t_v == 0 and not g_v <= 0:
                    canPush = False
                    break

        if canPush and doPush:
            self.grid[gsv, gsh] += self.currentTetromino.matrix[tsv, tsh]

        return canPush

    def __closestShiftUpwards(self, numToMoveBy):

        closest = -1 # Can't shift

        for i in range(numToMoveBy + 1):
            translation = np.array([[0, -(numToMoveBy - i)]])
            
            if self.canPlaceOnGrid(self.currentTetromino.matrix, self.currentTetromino.pos - translation):
                closest = numToMoveBy - i
            else:
                break

        return closest


    def __addGarbageLines(self, n):

        topOut = False
        for i in range(n):
            topOut = self.__moveAllLinesUp()

            if topOut:
                break

            self.grid[self.rows - 1].fill(self.garbageValue)
            # Make cheese
            self.grid[self.rows - 1][self.garbageRandom.integers(0, self.cols)] = 0

        if not topOut:

            # closestShift = self.__closestShiftUpwards(n)
            # if closestShift < 0:
            #     topOut = True

            # elif closestShift > 0:
            #     self.currentTetromino.translate(np.array([[0, -n]]))

            if self.canPlaceOnGrid(self.currentTetromino.matrix, self.currentTetromino.pos - np.array([[0, n]])):

                if not self.__closestShiftUpwards(n) == 0:
                    self.currentTetromino.translate(np.array([[0, -n]]))

            else:
                topOut = True

        return topOut

    def __moveAllLinesUp(self):

        topOut = not (self.grid[0] == 0).all()
        
        for i in range(0, self.rows - 1):
            
            self.grid[i] = np.copy(self.grid[i + 1])

        return topOut

    def __clearLines(self, clear = True):

        count = 0

        for idx, line in enumerate(self.grid):
            if (line > 0).all():

                if clear:
                    # This fill is probably redundant.
                    line.fill(0)
                    self.__moveLinesDown(idx)

                count += 1

        return count

    def __moveLinesDown(self, end):

        # First line is a new empty line
        prevRow = np.copy(self.grid[0])
        self.grid[0].fill(0)

        for i in range(1, end + 1):
            
            tmp = np.copy(self.grid[i])
            self.grid[i] = prevRow
            prevRow = tmp

    def __getSlicesFromGridOverlap(self):
        # Gets the overlapping slices between the grid and current tetromino matrix based on its position.

        oX, oY = self.currentTetromino.pos[0, 0], self.currentTetromino.pos[0, 1]

        gridSliceV = slice(max(0, oY), max(min(oY + self.currentTetromino.matrix.shape[0], self.grid.shape[0]), 0))
        gridSliceH = slice(max(0, oX), max(min(oX + self.currentTetromino.matrix.shape[1], self.grid.shape[1]), 0))

        tetrominoSliceV = slice(max(0, -oY), min(-oY + self.grid.shape[0], self.currentTetromino.matrix.shape[0]))
        tetrominoSliceH = slice(max(0, -oX), min(-oX + self.grid.shape[1], self.currentTetromino.matrix.shape[1]))

        return gridSliceV, gridSliceH, tetrominoSliceV, tetrominoSliceH

    def __getBag(self, bagSize):

        idx = self.__getSevenBag()

        for i in range(0, bagSize - 1):
            idx = np.concatenate((idx, self.__getSevenBag()))

        ts = [self.Tetromino(self.tetrominoMatrices, self.tetrominoStartPos, tag) for tag in idx]
    
        bag = deque(ts)
        
        return bag

    def __getSevenBag(self): 

        pieces = np.array([0, 1, 2, 3, 4, 5, 6])

        self.bagRandom.shuffle(pieces)

        return pieces

    def __rotateBag(self):
        nextTetromino = self.bag.popleft()

        # 7 As one piece is popped beforehand
        if len(self.bag) < 7:
              newPieces = self.__getSevenBag() 
              for tag in newPieces:
                self.bag.append(self.Tetromino(self.tetrominoMatrices, self.tetrominoStartPos, tag))

        return nextTetromino

    def __getTetrominoMatrices(self):
        return {
            # I
            0: np.array([[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]]),
            
            # J
            1: np.array([[2,0,0],[2,2,2],[0,0,0]]),

            # L
            2: np.array([[0,0,3],[3,3,3],[0,0,0]]),

            # O
            3: np.array([[4,4],[4,4]]),

            # S
            4: np.array([[0,5,5],[5,5,0],[0,0,0]]),

            # T
            5: np.array([[0,6,0],[6,6,6],[0,0,0]]),

            # Z
            6: np.array([[7,7,0],[0,7,7],[0,0,0]])
        }

    def getPositionsOfDropTiles(self):

        positions = []

        for (y,x), v in np.ndenumerate(self.grid):
            if v == 0:
                if y + 1 < self.rows:
                    if self.grid[y + 1, x] == 1:
                        positions.append( (y,x) )
                else: 
                    positions.append( (y,x) )

        return positions

    def saveState(self):
        
        state = TetrisGameState()

        state.lastDropClass = self.__lastDropClass
        state.currentReward = self.currentReward # Might be irrelevant
        state.pieceCount = self.pieceCount

        # Pts & Game over
        state.score = self.score
        state.lost = self.__lost

        # Grid information 
        state.grid = self.grid.copy()

        # Framerate related info
        state.tick = self.__tick
        state.frame = self.__frame
        state.lockTick = self.__lockTick

        # Combos
        state.comboCounterState = self.comboCounter.saveState()

        # DAS, ARR, SDF
        state.DAScharge = self.DAScharge

        state.ARRframeTick = self.ARRframeTick

        # Hold & Current piece
        state.currentTetrominoState = self.currentTetromino.saveState()
        if self.heldTetromino:
            state.heldTetrominoState = self.heldTetromino.saveState()
        state.heldLastPiece = self.heldLastPiece

        state.bagRandomState = self.bagRandom.bit_generator.state
        state.bagState = [t.saveState() for t in self.bag]

        # Garbage

        state.garbageRandomState = self.garbageRandom.bit_generator.state
        state.garbageState = self.garbage.saveState()

        return state

    def loadState(self, state):

        self.__lastDropClass = state.lastDropClass
        self.currentReward = state.currentReward
        self.pieceCount = state.pieceCount

        self.score = state.score
        self.__lost = state.lost

        # Grid information 
        self.grid = state.grid.copy()

        # Framerate related info
        self.__tick = state.tick
        self.__frame = state.frame
        self.__lockTick = state.lockTick

        # Combos
        self.comboCounter.loadState(state.comboCounterState)

        # DAS, ARR, SDF
        self.DAScharge = state.DAScharge

        self.ARRframeTick = state.ARRframeTick

        # Hold & Current piece
        self.currentTetromino = self.Tetromino.fromState(state.currentTetrominoState)
        if state.heldTetrominoState:
            self.heldTetromino = self.Tetromino.fromState(state.heldTetrominoState)
        else:
            self.heldTetromino = None
        self.heldLastPiece = state.heldLastPiece

        self.bagRandom.bit_generator.state = state.bagRandomState
        self.bag = deque()
        for tState in state.bagState:
            self.bag.append(self.Tetromino.fromState(tState))

        # Garbage

        self.garbageRandom.bit_generator.state = state.garbageRandomState
        self.garbage.loadState(state.garbageState)
