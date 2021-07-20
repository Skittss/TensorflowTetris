from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
from pygame.locals import *
from pygame_game_config import PygameHandlingConfig, PygameGameConfig
from pygame_interactive_config import PygameInteractiveConfig
from pygame_instance import PygameInstance

class Multiplayer:
    
    def __init__(self, gameConfig, p1InteractiveConfig, p2InteractiveConfig, p1HandlingConfig, p2HandlingConfig):

        self.p1 = PygameInstance(gameConfig, p1InteractiveConfig, p1HandlingConfig)
        self.p2 = PygameInstance(gameConfig, p2InteractiveConfig, p2HandlingConfig)

        self.gameConfig = gameConfig
        self.p1InteractiveConfig = p1InteractiveConfig
        self.p2InteractiveConfig = p2InteractiveConfig

        self.timer = None
        self.dt = 0
        self.updateInterval = 1 / self.gameConfig.frameRate

    def start(self):

        pygame.init()
        x1, y1 = self.p1InteractiveConfig.windowDimensions
        x2, y2 = self.p2InteractiveConfig.windowDimensions
        self.screen = pygame.display.set_mode((x1 + x2, y1),HWSURFACE|DOUBLEBUF)
        pygame.display.set_caption(self.p1InteractiveConfig.windowCaption)
        self.clock = pygame.time.Clock()

        self.p1.initialize(init=False)
        self.p2.initialize(init=False)

        self.dt = 0

        self.exited = False
        while not self.exited:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()

                if event.type == pygame.KEYDOWN:
                    self.__on_press(event.key)

                if event.type == pygame.KEYUP:
                    self.__on_release(event.key)

            self.dt += self.clock.get_time()

            if self.dt > self.updateInterval:
                self.doLoops()
                _, self.dt = divmod(self.dt, self.updateInterval)

            self.display()
            pygame.display.update()
            self.clock.tick(self.gameConfig.frameRate)

    def exit(self):

        self.p1.exit()
        self.p2.exit()

        if self.timer:
            self.timer.cancel()

        self.exited = True

    def doLoops(self, output=False):

        self.p1.loop(output=False, garbageTarget=self.p2.garbageFunc)
        self.p2.loop(output=False, garbageTarget=self.p1.garbageFunc)

        if output:
            self.display()

    def __on_press(self, key):
        self.p1.on_press(key)
        # self.p2.on_press(key)

    def __on_release(self, key):
        self.p1.on_release(key)
        # self.p2.on_release(key)

    def display(self):

        surface1 = self.p1.getSurface().convert_alpha()
        surface2 = self.p2.getSurface().convert_alpha()

        self.screen.blit(surface1, (0, 0))
        x, _ = self.p1InteractiveConfig.windowDimensions
        self.screen.blit(surface2, (x, 0))

if __name__ == "__main__":

    g = Multiplayer(PygameGameConfig, PygameInteractiveConfig, PygameInteractiveConfig, PygameHandlingConfig, PygameHandlingConfig)
    g.start()