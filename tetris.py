import numpy as np
import math
from enum import Enum
from collections import deque

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

## Redundant - Remove.
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

        def __init__(self, matrices, startPos = np.zeros([1, 2]), tag = 0):

            self.tag = tag
            self.startPos = startPos
            self.pos = startPos
            self.matrix = matrices[tag]
            self.rotateState = 0

        def resetPos(self):
            
            self.pos = self.startPos

        def rotate(self, k = 1):

            self.matrix = np.rot90(self.matrix, k)
            self.rotateState = (self.rotateState + k) % 4

        def getRotatedMatrix(self, k = 1):

            mat = np.rot90(self.matrix, k)
            nextRotateState = (self.rotateState + k) % 4
            return nextRotateState, mat

        def translate(self, vector):
            self.pos = np.add(self.pos, vector)

        def __str__(self):

            return f"<Tetromino: {self.tag}-piece>"
            

    def __init__(self, cols = 10, rows = 20, bagSize = 2, seed = 132, substeps = 5):

        self.__substep = 0
        
        self.score = 0

        self.__lost = False

        # Grid information
        self.cols = cols
        self.rows = rows
        self.grid = np.zeros([rows, cols])

        # Framerate related info
        self.substepsPerStep = substeps
        self.softdropSubsteps = 3

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
        self.__wallKickTestsI = {
            "01": np.array([[0,0], [-1,0], [-1,-1], [0, 2], [-1, 2]]),
            "10": np.array([[0,0], [1, 0], [ 1, 1], [0,-2], [ 1,-2]]),
            "12": np.array([[0,0], [1, 0], [ 1, 1], [0,-2], [ 1,-2]]),
            "21": np.array([[0,0], [-1,0], [-1,-1], [0, 2], [-1, 2]]),
            "23": np.array([[0,0], [1, 0], [ 1,-1], [0, 2], [ 1, 2]]),
            "32": np.array([[0,0], [-1,0], [-1, 1], [0,-2], [-1,-2]]),
            "30": np.array([[0,0], [-1,0], [-1, 1], [0,-2], [-1,-2]]),
            "03": np.array([[0,0], [1, 0], [ 1,-1], [0, 2], [ 1, 2]]),

            "02": np.array([[0,0], [-1, 0], [-2, 0], [ 1, 0], [ 2, 0]]),
            "20": np.array([[0,0], [ 0, 1], [ 0,-1], [ 0,-2], [ 0, 2]]),
            "13": np.array([[0,0], [ 1, 0], [ 2, 0], [-1, 0], [-2, 0]]),
            "31": np.array([[0,0], [ 0, 1], [ 0,-1], [ 0,-2], [ 0, 2]])
        }

        self.__wallKickTestsO = np.array([[0,0]])

        self.__wallKickTestsOther = {
            "01": np.array([[0,0], [-2,0], [1, 0], [-2, 1], [ 1,-2]]),
            "10": np.array([[0,0], [2, 0], [-1,0], [ 2,-1], [-1, 2]]),
            "12": np.array([[0,0], [-1,0], [2 ,0], [-1,-2], [ 2, 1]]),
            "21": np.array([[0,0], [1, 0], [-2,0], [ 1, 2], [-2,-1]]),
            "23": np.array([[0,0], [2, 0], [-1,0], [ 2,-1], [-1, 2]]),
            "32": np.array([[0,0], [-2,0], [1, 0], [-2, 1], [ 1,-2]]),
            "30": np.array([[0,0], [1, 0], [-2,0], [ 1, 2], [-2,-1]]),
            "03": np.array([[0,0], [-1,0], [2, 0], [-1,-2], [ 2, 1]]),

            "02": np.array([[0,0], [ 0,-1], [ 1,-1], [-1,-1], [ 1, 0], [-1, 0]]),
            "20": np.array([[0,0], [ 0, 1], [-1, 1], [ 1, 1], [-1, 0], [ 1, 0]]),
            "13": np.array([[0,0], [ 1, 0], [ 1,-2], [ 1,-1], [ 0,-2], [ 0,-1]]),
            "31": np.array([[0,0], [-1, 0], [-1,-2], [-1,-1], [ 0,-2], [ 0,-1]]),
        }



        self.__getNextTetromino()
        

    def display(self):
        print(self.grid)

    def __str__(self):

        string = str(self.grid).replace('[',"").replace(']',"").replace('.',"").split("\n")

        MINPAD = 5  # minimum horizontal padding
        N = MINPAD + 10 # total characters

        UIVERTICALPAD = 1
        PIECEPAD = 1

        padding = " "*N
        for i, line in enumerate(string):
            if i > 0:
                l = line[1:]
            else:
                l = line

            string[i] = padding + l + padding

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
        for piece in self.bag:
            
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

        # string 

        return "\n\n" + "\n".join(string)

    def nextState(self, actions):

        if not self.__lost:

            self.__popCurrentTetrominoFromGrid()

            downwardMoveCount = self.__updateSubstep(actions)

            self.__doActions(actions)

            pieceDropped = self.__attemptDownwardMoves(downwardMoveCount)

            self.__pushCurrentTetrominoToGrid()

            if pieceDropped:

                self.heldLastPiece = False

                self.__clearLines()

                self.__lost = not self.__getNextTetromino()

        else:
            #print("game over")
            return False

    def __updateSubstep(self, actions):
        # Update the substep; If hard-drop, go to next full step, If soft drop, increment multiple times

        if actions[Action.HardDrop]:
            self.__substep = 0
            return -1

        if actions[Action.SoftDrop]:
            downMoves, self.__substep = divmod(self.__substep + self.softdropSubsteps, self.substepsPerStep)
            return downMoves

        downMoves, self.__substep = divmod(self.__substep + 1, self.substepsPerStep)
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


    def __moveLeft(self):

        canMoveLeft = True

        for x in range(0, self.currentTetromino.matrix.shape[0]):
            for y in range(0, self.currentTetromino.matrix.shape[1]):

                if not self.currentTetromino.matrix[y, x] == 0:

                    pos = self.currentTetromino.pos + np.array([[x - 1, y]])

                    if pos[0, 0] < 0:
                        canMoveLeft = False
                        break

                    leftTile = self.grid[pos[0, 1], pos[0, 0]]
                    if not leftTile == 0:
                        canMoveLeft = False
                        break

        if canMoveLeft:
            self.currentTetromino.translate(np.array([[-1, 0]]))

    def __moveRight(self):

        canMoveRight = True

        for x in range(0, self.currentTetromino.matrix.shape[0]):
            for y in range(0, self.currentTetromino.matrix.shape[1]):
                
                if not self.currentTetromino.matrix[y, x] == 0:

                    pos = self.currentTetromino.pos + np.array([[x + 1, y]])

                    if pos[0, 0] >= self.cols:
                        canMoveRight = False
                        break

                    leftTile = self.grid[pos[0, 1], pos[0, 0]]
                    if not leftTile == 0:
                        canMoveRight = False
                        break
                
        if canMoveRight:
            self.currentTetromino.translate(np.array([[1, 0]]))


    def __rotateLeft(self):
        self.__doRotation(1)

    def __rotateRight(self):
        self.__doRotation(3)

    def __rotate180(self):
        self.__doRotation(2)

    def __doRotation(self, k):

        translation = self.__canRotate(k)

        if not type(translation) == type(None):
            self.currentTetromino.rotate(k)
            self.currentTetromino.translate(translation)

    def __canRotate(self, k):

        nextRotateState, rotatedMatrix = self.currentTetromino.getRotatedMatrix(k)

        for testTranslation in self.__getWallKickTests(nextRotateState):
            if self.__canPlaceOnGrid(rotatedMatrix, self.currentTetromino.pos + testTranslation):
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
        # Could possibly replace canMoveLeft & Right functions with this function.

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

            # Reset pos of current piece
            self.currentTetromino.resetPos()

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

    def __attemptDownwardMoves(self, count):
        
        canMoveDown = True

        for x in range(0, self.currentTetromino.matrix.shape[1]):
            for y in range(0, self.currentTetromino.matrix.shape[0]):

                if not self.currentTetromino.matrix[y, x] == 0:

                    pos = self.currentTetromino.pos + np.array([[x, y + 1]])

                    if pos[0, 1] >= self.rows:
                        canMoveDown = False
                        break

                    belowTile = self.grid[pos[0, 1], pos[0, 0]]
                    if not belowTile == 0:
                        canMoveDown = False
                        break
                
        if canMoveDown:

            if (not count == 0):
                self.currentTetromino.translate(np.array([[0, 1]]))

            if (count > 1):
                dropped = self.__attemptDownwardMoves(count - 1)
                return dropped

            elif (count < 0):
                dropped = self.__attemptDownwardMoves(count)
                return dropped
            
        return not canMoveDown

    def __getNextTetromino(self):
        self.currentTetromino = self.__rotateBag()
        return self.__pushCurrentTetrominoToGrid()
        
    def __popCurrentTetrominoFromGrid(self):
        
        gsv, gsh, tsv, tsh = self.__getSlicesFromGridOverlap()

        self.grid[gsv, gsh] -= self.currentTetromino.matrix[tsv, tsh]

    def __pushCurrentTetrominoToGrid(self):

        gsv, gsh, tsv, tsh = self.__getSlicesFromGridOverlap()

        #############################################
        canPush = True

        for g, t in zip(self.grid[gsv, gsh], self.currentTetromino.matrix[tsv, tsh]):
            for g_v, t_v in zip(g, t):
                if not t_v == 0 and not g_v == 0:
                    canPush = False
                    break

        if canPush:
            self.grid[gsv, gsh] += self.currentTetromino.matrix[tsv, tsh]

        return canPush

    def __clearLines(self):

        for idx, line in enumerate(self.grid):
            if (line > 0).all():
                # This fill is probably redundant.
                line.fill(0)
                self.__moveLinesDown(idx)

    def __moveLinesDown(self, end):

        # First line is a new empty line
        prevRow = np.copy(self.grid[0])
        self.grid[0].fill(0)
        # Ensure this is not a reference, might need a clone.

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

        # ts = [self.Tetromino(self.tetrominoMatrices, self.tetrominoStartPos, tag)
        #       for tag in self.bagRandom.integers(low = 0, high = 7, size = bagSize)]

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

        # self.bagRandom.integer(low = 0, high = len(pieces))


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

# ac = getEmptyActionObj()
# ac[Action.Left] = True

# tet = Tetris()

# for i in range(0, 10):
#     tet.display()
#     tet.nextState(ac)

