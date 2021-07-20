from os import environ, path
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
from pygame import Vector2, gfxdraw
from pygame.locals import *
from game_instance import GameInstance
from pygame_game_config import PygameGameConfig, PygameHandlingConfig
from pygame_interactive_config import PygameInteractiveConfig
import numpy as np
from math import ceil
from util import Action, lerpBlendRGBA, hexstrToRGB

# TODO:
#   ADD INDICATOR TO OVER 20 LINES GARBAGE

class PygameInstance(GameInstance):

    def __init__(self, gameConfig=PygameGameConfig, interactiveConfig=PygameInteractiveConfig, handlingConfig=PygameHandlingConfig):

        super().__init__(gameConfig=gameConfig, handlingConfig=handlingConfig)

        self.interactiveConfig = interactiveConfig

        self.keybindings = self.interactiveConfig.keybindings

        self.keyInfo = {
            self.keybindings[Action.Left]:          {"prev": False, "cur": False},
            self.keybindings[Action.Right]:         {"prev": False, "cur": False},
            self.keybindings[Action.SoftDrop]:      {"prev": False, "cur": False},
            self.keybindings[Action.HardDrop]:      {"prev": False, "cur": False},
            self.keybindings[Action.RotateLeft]:    {"prev": False, "cur": False},
            self.keybindings[Action.RotateRight]:   {"prev": False, "cur": False},
            self.keybindings[Action.Rotate180]:     {"prev": False, "cur": False},
            self.keybindings[Action.Hold]:          {"prev": False, "cur": False}

        }

        self.clock = None
        self.updateInterval = 1/gameConfig.frameRate
        self.dt = 0
        self.lastDropPrompt = None

    def setDisplayOffset(self, x, y):
        self.displayOffset = [x, y]

    def __getGridDiv(self, parentRect, HEIGHT = 0.8):
        return pygame.Rect(0, 0, parentRect.w, parentRect.h * HEIGHT)

    def __getGridRect(self, displayData, parentRect, HEIGHT = 0.8):

        gridHeight = HEIGHT * parentRect.h
        gridWidth = (gridHeight / displayData.hiddenRows) * displayData.grid.shape[1]

        rect = pygame.Rect(0, 0, gridWidth, gridHeight)
        rect.center = parentRect.center

        return rect

    def __getCenteredSubRect(self, parentRect, SIZE=0.8):

        rect = pygame.Rect(0, 0, parentRect.w * SIZE, parentRect.h * SIZE)
        rect.center = parentRect.center

        return rect

    def __divideRect(self, parentRect, divisions, axis=1, SQUARE=True):

        rects = []
        if divisions > 0:
            if axis == 0:
                # Horizontal
                width = parentRect.w / divisions
                height = width if SQUARE else parentRect.h

                for i in range(divisions):

                    r = Rect(0, 0, width, height)
                    r.centery = parentRect.centery
                    r.left = parentRect.left if i == 0 else rects[i - 1].right


                    rects.append(r)
                
            else:
                # Vertical
                height = parentRect.h / divisions
                width = height if SQUARE else parentRect.w

                for i in range(divisions):

                    r = Rect(0, 0, width, height)
                    r.centerx = parentRect.centerx
                    r.top = parentRect.top if i == 0 else rects[i - 1].bottom

                    rects.append(r)

        return rects

    def __getHoldTextContainerRect(self, fontRect, relativeRect, WIDTH = 0.5):

        rect = pygame.Rect(0, 0, relativeRect.w * WIDTH, fontRect.h)
        rect.topright = relativeRect.topleft

        return rect

    def __getHoldContainerRect(self, relativeRect, underRect, WIDTH = 0.5):

        dim = relativeRect.w * WIDTH

        rect = pygame.Rect(0, 0, dim, dim)
        rect.topright = underRect.bottomright
        
        return rect

    def __getComboRect(self, relativeRect):

        rect = pygame.Rect(0, 0, relativeRect.w, relativeRect.h)
        rect.topleft = relativeRect.bottomleft

        return rect

    def __getGarbageIndicatorRect(self, relativeRect, WIDTH = 0.05):

        rect = pygame.Rect(0, 0, relativeRect.w * WIDTH, relativeRect.h)#
        rect.topleft = relativeRect.topright

        return rect

    def __getGarbageLinesIndicator(self, displayData, parentRect):

        height = min(parentRect.h, (parentRect.h / displayData.hiddenRows) * displayData.pendingGarbage)

        rect = pygame.Rect(0, 0, parentRect.w, height)
        rect.bottomleft = parentRect.bottomleft

        return rect

    def __getBagTextContainerRect(self, fontRect, relativeSizeRect, relativePosRect, WIDTH = 0.5):

        rect = pygame.Rect(0, 0, relativeSizeRect.w * WIDTH, fontRect.h)
        rect.topleft = relativePosRect.topright

        return rect

    def __getBagRect(self, relativeSizeRect, relativePosRect, WIDTH = 0.5, HEIGHT = 0.85):

        rect = pygame.Rect(0, 0, relativeSizeRect.w * WIDTH, relativeSizeRect.h * HEIGHT)
        rect.topleft = relativePosRect.bottomleft

        return rect

    def __drawGrid(self, surface, displayData, matrix, parentRect, gridLines=False, divisions=0, rectAxis=0, ghostData=None):

        offset = 0
        if rectAxis == 0:
            # Width
            if divisions > 0:
                cellDim = parentRect.w / divisions
                offset = (max(0, divisions - matrix.shape[1]) * cellDim) / 2
            else:
                cellDim = parentRect.w / matrix.shape[1]

        else:
            #Height
            if divisions > 0:
                cellDim = parentRect.h / divisions
                offset = (max(0, divisions - matrix.shape[0]) * cellDim) / 2

            else:
                cellDim = parentRect.h / matrix.shape[0]

        if gridLines:
            for y in range(matrix.shape[0] - 1):

                yOffset = parentRect.top + (1 + y) * cellDim
                pygame.draw.line(
                    surface, self.interactiveConfig.gridDivisorColor,
                    Vector2(parentRect.left, yOffset), 
                    Vector2(parentRect.right-1, yOffset),
                    width=self.interactiveConfig.gridDivisorWidth
                )
            
            for x in range(matrix.shape[1] - 1):
                xOffset = parentRect.left + (1 + x) * cellDim
                pygame.draw.line(
                    surface, self.interactiveConfig.gridDivisorColor,
                    Vector2(xOffset, parentRect.top), 
                    Vector2(xOffset, parentRect.bottom-1),
                    width=self.interactiveConfig.gridDivisorWidth
                )

        rect = Rect(0, 0, ceil(cellDim), ceil(cellDim))
        if ghostData:
            ghostPos, ghostMatrix = ghostData
            # Could remove overlap error by drawing from right -> left, top -> bottom
            for (y, x), cell in np.ndenumerate(ghostMatrix):

                if cell in self.interactiveConfig.colorTable:
                    if 0 <= ghostPos[0, 0] + x < displayData.grid.shape[1] and 0 <= ghostPos[0, 1] + y < displayData.hiddenRows:
                        rect.top = parentRect.top + cellDim * (ghostPos[0, 1] + y)
                        rect.left = parentRect.left + cellDim * (ghostPos[0, 0] + x)

                        pygame.draw.rect(
                        surface, 
                        lerpBlendRGBA(
                            self.interactiveConfig.gridBackgroundColor, 
                            hexstrToRGB(self.interactiveConfig.colorTable[cell]), 
                            self.interactiveConfig.ghostAlpha
                        ),
                        rect
                )

        for (y, x), cell in np.ndenumerate(matrix):
            
            color = None
            if cell == displayData.garbageValue:
                color = self.interactiveConfig.garbageColor
            elif cell in self.interactiveConfig.colorTable:
                color = self.interactiveConfig.colorTable[cell]

            if color:
                rect.top = offset + parentRect.top + cellDim * y
                rect.left = offset + parentRect.left + cellDim * x
                pygame.draw.rect(
                    surface, color,
                    rect
                )

    def __drawRectOutline(self, surface, rect, color, width=1):
        x, y, w, h = rect
        width = max(width, 1)  # Draw at least one rect.
        width = min(min(width, w//2), h//2)  # Don't overdraw.

        # This draws several smaller outlines inside the first outline. Invert
        # the direction if it should grow outwards.
        for i in range(width):
            gfxdraw.rectangle(surface, (x+i, y+i, w-i*2, h-i*2), color)

    def getSurface(self):

        displayData = self.tet.getDisplayData()

        surface = pygame.Surface(self.interactiveConfig.gameDimensions, SRCALPHA).convert_alpha()
        surfaceRect = surface.get_rect()
        surface.fill(self.interactiveConfig.colorSwatch[0])

        holdText = self.font.render("HOLD", 1, pygame.Color('black'))
        holdTextRect = holdText.get_rect()

        bagText = self.font.render("NEXT", 1, pygame.Color('black'))
        bagTextRect = bagText.get_rect()

        # fpsStr = self.font.render(str(self.tet.DAScharge), 1, pygame.Color('black'))
        # pos = fpsStr.get_rect()
        # pos.topleft = (0, 0)

        gridDiv = self.__getGridDiv(surfaceRect)
        gridRect = self.__getGridRect(displayData, gridDiv)

        holdTextContainerRect = self.__getHoldTextContainerRect(holdTextRect, gridRect)
        holdTextRect.center = holdTextContainerRect.center

        holdContainerRect = self.__getHoldContainerRect(gridRect, holdTextContainerRect)
        holdRect = self.__getCenteredSubRect(holdContainerRect)

        comboRect = self.__getComboRect(holdContainerRect)
        if displayData.combo > 0:
            comboText = self.font.render(f"Combo x{displayData.combo}!", 1, pygame.Color('black'))
            comboTextRect = comboText.get_rect()
            comboTextRect.centery = comboRect.centery
            comboTextRect.right = comboRect.right

        garbageIndicatorRect = self.__getGarbageIndicatorRect(gridRect)
        garbageLinesIndicator = self.__getGarbageLinesIndicator(displayData, garbageIndicatorRect)

        bagTextContainerRect = self.__getBagTextContainerRect(bagTextRect, gridRect, garbageIndicatorRect)
        bagTextRect.center = bagTextContainerRect.center
        
        bagRect = self.__getBagRect(gridRect, bagTextContainerRect)
        bagRects = [self.__getCenteredSubRect(r) for r in self.__divideRect(bagRect, displayData.preview)]

        scoreText = self.font.render(f"{displayData.score}pts", 1, pygame.Color('black'))
        scoreTextRect = scoreText.get_rect()
        scoreTextRect.top = gridRect.bottom
        scoreTextRect.centerx = gridRect.centerx

        try:
            self.lastDropPrompt = f"{self.interactiveConfig.promptTable[displayData.lastDropType]} ({self.gameConfig.scoreTable[displayData.lastDropType]})"
            lineclearText = self.font.render(self.lastDropPrompt, 1, pygame.Color('black'))

        except KeyError:
            if self.lastDropPrompt:
                lineclearText = self.font.render(f"{self.lastDropPrompt}", 1, pygame.Color('black'))
            else:
                lineclearText = self.font.render(f" ", 1, pygame.Color('black'))


        lineclearTextRect = lineclearText.get_rect()
        lineclearTextRect.top = scoreTextRect.bottom
        lineclearTextRect.centerx = scoreTextRect.centerx

        pygame.draw.rect(
            surface, self.interactiveConfig.gridBackgroundColor, 
            gridRect
        )

        self.__drawGrid(
            surface, displayData, displayData.grid[displayData.hiddenRows:], gridRect, 
            gridLines=True,
            ghostData=(displayData.ghostPos, displayData.currentTetrominoMatrix))

        self.__drawRectOutline(surface, gridRect, self.interactiveConfig.gridBorderColor, self.interactiveConfig.gridBorderThickness)

        surface.blit(holdText, holdTextRect)

        if displayData.heldTetromino:
            self.__drawGrid(surface, displayData, displayData.heldTetromino.matrix, holdRect, divisions=4)

        # pygame.draw.rect(
        #     surface, self.interactiveConfig.colorSwatch[3], 
        #     comboRect
        # )

        if displayData.combo > 0:
            surface.blit(comboText, comboTextRect)

        # pygame.draw.rect(
        #     surface, self.interactiveConfig.colorSwatch[4], 
        #     garbageIndicatorRect
        # )

        pygame.draw.rect(
            surface, 
            self.interactiveConfig.garbageIndicatorColor if displayData.pendingGarbage <= displayData.hiddenRows else self.interactiveConfig.garbageIndicatorWarningColor, 
            garbageLinesIndicator
        )

        surface.blit(bagText, bagTextRect)

        for i, rect in enumerate(bagRects):
            self.__drawGrid(
                surface, displayData, displayData.bag[i].matrix,
                rect, divisions=4
            )

        surface.blit(scoreText, scoreTextRect)
        surface.blit(lineclearText, lineclearTextRect)

        # surface.blit(fpsStr, pos)

        return surface


    def display(self):

        surface = self.getSurface()
        self.screen.blit(surface, (0, 0))

    def initialize(self, init=True):

        self.displayOffset = [0, 0]
        pygame.init()

        if init:
            
            self.screen = pygame.display.set_mode(self.interactiveConfig.windowDimensions,HWSURFACE|DOUBLEBUF)
            pygame.display.set_caption(self.interactiveConfig.windowCaption)

            self.clock = pygame.time.Clock()

        self.font = pygame.font.Font(path.join(*self.interactiveConfig.relativeFontPath), 36)

    def beforeLoopHook(self):
        self.__getActionFromInputs()
        self.__forwardAllKeyStates()

    def run(self):

        self.initialize()

        self.dt = 0

        self.exited = False
        while not self.exited:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()

                elif event.type == pygame.KEYDOWN:
                    self.on_press(event.key)

                elif event.type == pygame.KEYUP:
                    self.on_release(event.key)

            self.dt += self.clock.get_time()

            if self.dt > self.updateInterval:
                self.loop(output=False)
                _, self.dt = divmod(self.dt, self.updateInterval)

            self.display()

            pygame.display.update()
            self.clock.tick(self.gameConfig.frameRate)

    def exit(self):
        self.exited = True

        if self.timer:
            self.timer.cancel()

        pygame.quit()

    def __getActionFromInputs(self):

        self.__doActionCheck(Action.Left, self.__isActionDown) 

        self.__doActionCheck(Action.Right, self.__isActionDown)

        self.__doActionCheck(Action.SoftDrop, self.__isActionDown)

        self.__doActionCheck(Action.RotateLeft, self.__isActionToggled)
        
        self.__doActionCheck(Action.RotateRight, self.__isActionToggled)

        self.__doActionCheck(Action.Rotate180, self.__isActionToggled)

        self.__doActionCheck(Action.Hold, self.__isActionToggled) 
  
        self.__doActionCheck(Action.HardDrop, self.__isActionToggled)

    def __forwardAllKeyStates(self):

        for k in self.keyInfo:
            self.keyInfo[k]["prev"] = self.keyInfo[k]["cur"]

    def __isActionToggled(self, action):
        return self.keyInfo[self.keybindings[action]]["cur"] and not self.keyInfo[self.keybindings[action]]["prev"]

    def __isActionDown(self, action):
        return self.keyInfo[self.keybindings[action]]["cur"]

    def __doActionCheck(self, action, checkFunc):

        if checkFunc(action):
            self.ac[action] = True
        else:
            self.ac[action] = False


    def __getKeyInfoDictKey(self, key):

        try:
            k = key.char

        except AttributeError:
            k = key

        return k

    def on_press(self, key):

        dictKey = self.__getKeyInfoDictKey(key)
        
        try: 
            keyEntry = self.keyInfo[dictKey]
            if keyEntry:
                keyEntry["prev"] = keyEntry["cur"]
                keyEntry["cur"] = True

        except KeyError: 
            return

    def on_release(self, key):
        
        dictKey = self.__getKeyInfoDictKey(key)

        try: 
            keyEntry = self.keyInfo[dictKey]
            if keyEntry:
                keyEntry["prev"] = keyEntry["cur"]
                keyEntry["cur"] = False

        except KeyError:
            return


if __name__ == "__main__":
    game = PygameInstance()
    game.run()