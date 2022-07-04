import sys

import pygame
from bin.files import load_image
from bin.gui import LevelMenu
from bin.game import Game, levels_list, boss_value
from bin.settings import screen_rect


class Main:
    def __init__(self, screen):
        self.screen = screen

        self.state = 'level'
        self.create_levels()

    def create_levels(self):
        self.levels = LevelMenu(self.screen, pygame.font.Font('font/Roboto-Medium.ttf', 32),
                                levels_list, self.load_level)

    def load_level(self, state, level):
        pygame.mixer.stop()
        self.game = Game(self, level, boss_value)
        self.state = state

    def fix_screen(self):
        if self.state == 'game':
            self.game.background_image = pygame.transform.scale(self.game.background_image,
                                                                self.screen.get_size())
            self.screen.blit(self.game.background_image, (0, 0))
        elif self.state == 'level':
            self.levels.background_image = pygame.transform.scale(self.levels.background_image,
                                                                  self.screen.get_size())
            self.screen.blit(self.levels.background_image, (0, 0))

    def run(self):
        if self.state == 'level':
            self.levels.run()
        elif self.state == 'game':
            self.game.run()


# Run
if __name__ == '__main__':
    # Pygame init
    pygame.init()
    pygame.font.init()
    pygame.mixer.pre_init(44100, 32, 2, 102)

    clock = pygame.time.Clock()  # Clock

    # Screen presets
    full_screen = False
    flags = pygame.DOUBLEBUF | pygame.HWSURFACE  # | pygame.RESIZABLE
    best_depth = pygame.display.mode_ok(screen_rect.size, flags, 32)

    app_screen = pygame.display.set_mode(size=screen_rect.size, flags=flags,
                                         depth=best_depth, display=0)
    pygame.display.set_icon(load_image('image/icon.png'))
    pygame.display.set_caption('EVA IN SPACE')

    main_run = Main(app_screen)

    while True:
        # Events
        for event in pygame.event.get():
            # Event quit
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # On resize
            if event.type == pygame.WINDOWRESIZED:
                main_run.fix_screen()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if main_run.state == 'game':
                        main_run.state = 'level'
                        main_run.create_levels()

                if event.key == pygame.K_F11:  # Change full screen
                    backup_screen = app_screen.copy()
                    if not full_screen:  # set full screen
                        flags = flags | pygame.FULLSCREEN
                        app_screen = pygame.display.set_mode(size=screen_rect.size, flags=flags,
                                                             depth=best_depth, display=0)
                    else:  # window
                        flags = pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE
                        app_screen = pygame.display.set_mode(size=screen_rect.size, flags=flags,
                                                             depth=best_depth, display=0)
                    app_screen.blit(backup_screen, (0, 0))
                    full_screen = not full_screen

        main_run.run()
        pygame.display.update()
