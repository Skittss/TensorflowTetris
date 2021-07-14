import numpy as np
import math
from util import Action, KeyIcons, ScoreTypes
from enum import Enum
from collections import deque
from config import GameConfig, HandlingConfig

# TODO      
#           ---Modify piece spawn positions to be correctly centered.
#           ---Point System
#           Show points from line clears above/below points
#           ---DAS, 
#           ---ARR,
#           ---SDF
#           ---Lock delay
#           ---Gravity - G, If moved more than one downwards in a single frame, re-do input? Maybe not for now.
#           ---Check spawn orientations. Reset orientation on hold.
#           ---Fix wall kicks.
#           ---Current actions displayed on __str__
#           Hidden rows
#           Add line clear type to __str__ i.e. tetris / t-spin mini etc.
#           Garbage meter with red # added to __str__
#           ---Ghost piece added to __str__

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

class Tetrominos(Enum):
    I = 0
    J = 1
    L = 2
    O = 3
    S = 4
    T = 5
    Z = 6

class Tetris:

    class Tetromino:

        def __init__(self, matrices, startPos, tag = 0, centreStartPos = True):



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

        def __str__(self):

            return f"<Tetromino: {self.tag}-piece>"
            
    def __init__(self, cols = 10, rows = 20, bagSize = 2, seed = 132, 
                    handlingConfig = HandlingConfig,
                    gameConfig = GameConfig
                ):

        # DEBUG
        self.lastDropClass = None
        
        # Pts & Game over
        self.score = 0
        self.__lost = False

        # Grid information 
        self.cols = cols
        self.rows = rows
        self.grid = np.zeros([rows, cols])

        # Framerate related info
        self.__tick = 0
        self.__frame = 0
        self.__G = gameConfig.G
        self.__frameRate = gameConfig.frameRate
        self.__lockDelay = gameConfig.lockDelay
        self.__lockTick = 0

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
        self.tetrominoStartPos = np.array([[math.floor(self.cols / 2),0]])

        # Bag
        self.bagRandom = np.random.default_rng(seed = seed)
        self.bag = self.__getBag(bagSize)

        # Wall kick tests - Could reduce hashmaps by noting "xy" == -"yx", but keep things simple for now.
        self.__wallKickTestsI = gameConfig.I_kicks

        self.__wallKickTestsO = gameConfig.O_kicks

        self.__wallKickTestsOther = gameConfig.Other_kicks

        self.__getNextTetromino()
        

    def display(self):
        print(self.grid)

    # def matchesTetrominoPart(self, c):
    #     try:
    #         v = int(c)
    #         return v >= 0

    #     except:
    #         return False

    # def __indexOfMatch(self, string, cmp, start = 0):
    #     for i, chr in enumerate(string[start:]):
    #         if cmp(chr):
    #             return i + start
        
    #     return -1

    # def __findNth(self, string, cmp, n):
    #     idx = 0
    #     for i in range(0, n):
    #         next = self.__indexOfMatch(string, cmp, start = idx)

    #         if next < 0:
    #             return -1

    #         idx = next + 1

    #     return idx - 1

    def __gridToStringList(self):

        return [[str(int(v)) for v in row] for row in self.grid]

    ## Consider moving this to another file after making another function which gives the necessary information to produce this output.
    def toString(self, MINPAD = 5, EXTRAPAD = 10, UIVERTICALPAD = 1, PIECEPAD = 1, ACTIONVERTPAD = 4, SHOWGHOST = True, GHOSTCHARACTER = "@"):

        # Get rid of all the garbage from numpy str. Perhaps consider implementing a faster version of this.
        string = self.__gridToStringList()
        # Add ghost piece:

        if SHOWGHOST:
            ghostPos = self.__findCurrentHarddropPosition()

            for i in range(0, len(self.currentTetromino.matrix)):
                matrixRow = self.currentTetromino.matrix[i]
                try:
                    row = string[ghostPos[0, 1] + i]

                    for (j,), v in np.ndenumerate(matrixRow):
                        if not v == 0 and row[ghostPos[0, 0] + j] == "0":
                            row[ghostPos[0, 0] + j] = GHOSTCHARACTER

                except IndexError:
                    pass
                    
        string = [f"█{' '.join(s)}█" for s in string] 
        string = ["▄"*len(string[0])] + string + ["▀"*len(string[0])]

        # Pad the grid, add Hold and Preview.

        N = MINPAD + EXTRAPAD # total characters

        padding = " "*N
        for i, line in enumerate(string):
            string[i] = padding + line + padding

        if len(string) < 8:
            for i in range (0, 8 - len(string)):
                string.append("\n")

        holdText = "Hold:"
        bagText = "Next:"
        string[UIVERTICALPAD] = string[UIVERTICALPAD][:N-len(holdText) - MINPAD] + holdText + string[UIVERTICALPAD][N - MINPAD:len(string[UIVERTICALPAD]) - N + MINPAD] + bagText + string[UIVERTICALPAD][len(string[UIVERTICALPAD]) - N + len(bagText) + MINPAD : len(string[UIVERTICALPAD])]

        if self.heldTetromino:

            # Can move this to function (albeit with quite a few params) for re-use below
            holdPieceMatrix = self.heldTetromino.matrix
            uiRow = UIVERTICALPAD + 1 + PIECEPAD
            for y in range(holdPieceMatrix.shape[1]):
                matrixRowStr = str(holdPieceMatrix[y])[1:-1].replace("0", " ")

                string[uiRow + y] = string[uiRow + y][:N-len(matrixRowStr) - MINPAD] + matrixRowStr + string[uiRow + y][N - MINPAD:len(string[uiRow + y])]


        uiRow = UIVERTICALPAD + 1 + PIECEPAD
        
        for i in range(0, 5):
            
            piece = self.bag[i]
            pieceMatrix = piece.matrix
            pieceRows = pieceMatrix.shape[1]
            rowsSkipped = 0
            
            if uiRow + pieceRows > self.grid.shape[0]:
                break

            for y in range(pieceRows):
                if np.all(pieceMatrix[y] == 0):
                    rowsSkipped += 1
                else:
                    matrixRowStr = str(pieceMatrix[y])[1:-1].replace("0", " ")
                    drawRow = uiRow + y - rowsSkipped

                    string[drawRow] = string[drawRow][:len(string[drawRow]) - N + MINPAD] + matrixRowStr + string[drawRow][len(string[drawRow]) - N + len(matrixRowStr) + MINPAD : len(string[drawRow])]

            uiRow += pieceRows + PIECEPAD - rowsSkipped

        # Add current actions:

        actionStr = [
            f"\t{KeyIcons.entries[Action.RotateLeft]}\t{KeyIcons.entries[Action.RotateRight]}\t{KeyIcons.entries[Action.Rotate180]}\t\t{KeyIcons.entries[Action.Hold]}\t{KeyIcons.entries[Action.Left]}\t\t{KeyIcons.entries[Action.Right]}",
            f"\t\t\t\t\t\t\t{KeyIcons.entries[Action.SoftDrop]}",
            f"\t\t\t\t\t{KeyIcons.entries[Action.HardDrop]}"
        ]

        for i in range(0, len(actionStr)):
            string[ACTIONVERTPAD + i] += actionStr[i]

        return "\n\n" + "\n".join(string) + f"\n\nFrame: {self.__frame}ff \tTick: {self.__tick}fff\tDAS Charge: {self.DAScharge}fff\tARR Frame tick: {self.ARRframeTick}fff\tLock tick: {self.__lockTick}fff\nDrop Hover: {ghostPos}ffffff\tPiece Pos: {self.currentTetromino.pos}ffffff\tLast move was rotate: {self.currentTetromino.lastMoveWasRotate}fffff\nScore: {self.score}fffff"

    def nextState(self, actions):

        if not self.__lost:

            self.__doDASandARRreset(actions)

            self.__popCurrentTetrominoFromGrid()

            downwardMoveCount = self.__updateTick(actions)

            self.__doActions(actions)

            pieceDropped = self.__attemptDownwardMoves(downwardMoveCount)

            self.__pushCurrentTetrominoToGrid()

            if pieceDropped:

                self.__lockTick = 0

                self.heldLastPiece = False

                # Don't actually clear lines the first time around else it messes up the classification
                linesCleared = self.__clearLines(clear = False)

                self.score += GameConfig.scoreTable[self.__classifyDrop(linesCleared)]

                self.__clearLines()

                self.__lost = not self.__getNextTetromino()

            self.__frame = (self.__frame + 1) % self.__frameRate

        else:
            return False

    def __withinGrid(self, pos):
        return 0 < pos[0, 0] < self.cols and 0 < pos[0, 1] < self.rows

    def __isOccupied(self, pos):
        if not self.__withinGrid(pos):
            return True

        check1 = self.grid[self.currentTetromino.pos[0, 1]]
        check = self.grid[self.currentTetromino.pos[0, 1], self.currentTetromino.pos[0, 0]]
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

    def __classifyDrop(self, linesCleared):

        if linesCleared == 4:
            return ScoreTypes.Tetris

        if linesCleared == 0:
            base = ScoreTypes.Drop
        elif linesCleared == 1:
            base = ScoreTypes.Single
        elif linesCleared == 2:
            base = ScoreTypes.Double
        else:
            base = ScoreTypes.Triple

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

    def __canMoveOnCurrentFrame(self):
        return self.DAScharge == 0 or (abs(self.DAScharge) == self.DAS and (self.ARRframeTick == self.ARR - 1 or self.ARR == 0))

    def __doMove(self, translation):
        canMove = self.__canPlaceOnGrid(self.currentTetromino.matrix, self.currentTetromino.pos + np.array([translation]))

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

        if self.__canMoveOnCurrentFrame():

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
            if self.__canPlaceOnGrid(rotatedMatrix, self.currentTetromino.pos + testTranslation):

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

    def __canPlaceOnGrid(self, matrix, pos):

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

    def __rotateBag(self):
        nextTetromino = self.bag.popleft()

        # 7 As one piece is popped beforehand
        if len(self.bag) < 7:
              newPieces = self.__getSevenBag() 
              for tag in newPieces:
                self.bag.append(self.Tetromino(self.tetrominoMatrices, self.tetrominoStartPos, tag))

        return nextTetromino

    def __findCurrentHarddropPosition(self):

        self.__popCurrentTetrominoFromGrid()

        downMoves = 0
        canMoveDown = True

        while canMoveDown:
            canMoveDown = self.__canPlaceOnGrid(self.currentTetromino.matrix, self.currentTetromino.pos + np.array([[0, downMoves]]))

            if canMoveDown:
                downMoves += 1

        self.__pushCurrentTetrominoToGrid()

        return self.currentTetromino.pos + np.array([[0, downMoves - 1]])

    def __attemptDownwardMoves(self, count):
        
        canMoveDown = self.__canPlaceOnGrid(self.currentTetromino.matrix, self.currentTetromino.pos + np.array([[0, 1]]))
                
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

    def __pushCurrentTetrominoToGrid(self):

        gsv, gsh, tsv, tsh = self.__getSlicesFromGridOverlap()

        canPush = True

        for g, t in zip(self.grid[gsv, gsh], self.currentTetromino.matrix[tsv, tsh]):
            for g_v, t_v in zip(g, t):
                if not t_v == 0 and not g_v == 0:
                    canPush = False
                    break

        if canPush:
            self.grid[gsv, gsh] += self.currentTetromino.matrix[tsv, tsh]

        return canPush

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