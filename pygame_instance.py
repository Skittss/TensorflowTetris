from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
from pygame import Vector2, gfxdraw
from pygame.locals import *
from game_instance import GameInstance
from game_config import GameConfig, HandlingConfig
from pygame_interactive_config import PygameInteractiveConfig
import numpy as np
from math import ceil

# TODO:
#       Separate update loop from pygame event loop. Inputs can update based on the framerate however
#           the game should be separate at a fixed update rate.

class PygameInstance(GameInstance):

    def __init__(self, gameConfig=GameConfig, interactiveConfig=PygameInteractiveConfig, handlingConfig=HandlingConfig):

        super().__init__(gameConfig=gameConfig, handlingConfig=handlingConfig)

        self.interactiveConfig = interactiveConfig

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

    def __getHoldRect(self, relativeRect, WIDTH = 0.5):

        dim = relativeRect.w * WIDTH

        rect = pygame.Rect(0, 0, dim, dim)
        rect.topright = relativeRect.topleft
        
        return rect

    def __getComboRect(self, relativeRect):

        rect = pygame.Rect(0, 0, relativeRect.w, relativeRect.h)
        rect.topleft = relativeRect.bottomleft

        return rect

    def __getGarbageIndicatorRect(self, relativeRect, WIDTH = 0.05):

        rect = pygame.Rect(0, 0, relativeRect.w * WIDTH, relativeRect.h)#
        rect.topleft = relativeRect.topright

        return rect

    def __getBagRect(self, relativeSizeRect, relativePosRect, WIDTH = 0.5, HEIGHT = 0.85):

        rect = pygame.Rect(0, 0, relativeSizeRect.w * WIDTH, relativeSizeRect.h * HEIGHT)
        rect.topleft = relativePosRect.topright

        return rect

    def __drawGrid(self, surface, displayData, matrix, parentRect, rectAxis=0):
        
        if rectAxis == 0:
            # Width
            cellDim = parentRect.w / matrix.shape[1]

        else:
            #Height
            cellDim = parentRect.h / matrix.shape[0]

        for y in range(matrix.shape[0] - 1):

            yOffset = parentRect.top + (1 + y) * cellDim
            pygame.draw.line(
                surface, self.interactiveConfig.gridDivisorColor,
                Vector2(parentRect.left, yOffset), 
                Vector2(parentRect.right, yOffset),
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

        for (y, x), cell in np.ndenumerate(matrix):
            
            color = None
            if cell == displayData.garbageValue:
                color = self.interactiveConfig.garbageColor
            elif cell in self.interactiveConfig.colorTable:
                color = self.interactiveConfig.colorTable[cell]

            if color:
                rect = Rect(0, 0, ceil(cellDim), ceil(cellDim))
                rect.top = parentRect.top + cellDim * y
                rect.left = parentRect.left + cellDim * x
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
        fpsStr = self.font.render(str(self.timer.get_fps()), 1, pygame.Color('black'))
        pos = fpsStr.get_rect()
        pos.topleft = (0, 0)

        gridDiv = self.__getGridDiv(surfaceRect)
        gridRect = self.__getGridRect(displayData, gridDiv)

        holdRect = self.__getHoldRect(gridRect)
        comboRect = self.__getComboRect(holdRect)

        garbageIndicatorRect = self.__getGarbageIndicatorRect(gridRect)

        bagRect = self.__getBagRect(gridRect, garbageIndicatorRect)

        pygame.draw.rect(
            surface, self.interactiveConfig.gridBackgroundColor, 
            gridRect
        )

        self.__drawGrid(surface, displayData, displayData.grid[displayData.hiddenRows:], gridRect)

        self.__drawRectOutline(surface, gridRect, self.interactiveConfig.gridBorderColor, self.interactiveConfig.gridBorderThickness)

        pygame.draw.rect(
            surface, self.interactiveConfig.colorSwatch[2], 
            holdRect
        )

        pygame.draw.rect(
            surface, self.interactiveConfig.colorSwatch[3], 
            comboRect
        )

        pygame.draw.rect(
            surface, self.interactiveConfig.colorSwatch[4], 
            garbageIndicatorRect
        )

        pygame.draw.rect(
            surface, self.interactiveConfig.colorSwatch[2], 
            bagRect
        )

        surface.blit(fpsStr, pos)

        return surface


    def display(self):

        surface = self.getSurface()
        self.screen.blit(surface, (0, 0))


    def initialize(self):

        self.displayOffset = [0, 0]

        pygame.init()
        self.screen = pygame.display.set_mode(self.interactiveConfig.windowDimensions,HWSURFACE|DOUBLEBUF)
        pygame.display.set_caption(self.interactiveConfig.windowCaption)
        self.timer = pygame.time.Clock()

        self.font = pygame.font.Font(None, 36)

    def run(self):

        self.initialize()

        self.exited = False
        while not self.exited:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exited = True

            self.loop()

            pygame.display.update()
            self.timer.tick(self.gameConfig.frameRate)

    def exit(self):
        self.exited = True
        pygame.quit()



if __name__ == "__main__":
    game = PygameInstance()
    game.run()