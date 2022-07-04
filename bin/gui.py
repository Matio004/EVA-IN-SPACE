from typing import Union
from random import choice

import pygame

from .files import load_image, load_sound
from .groups import all_group, clear
from .settings import screen_width
from .sprites import Title, Image
from .images_modification import ImageMod


# Skill bar
class GuiBar:
    def __init__(self, start: str, middle: str, end: str, bar_color: str,
                 bar_rect_top_left: Union[list, tuple], max_bar_width: int, bar_height: int,
                 pos: Union[list[int, int], tuple[int, int]], bar_bg=None):
        # Bar
        self.pos_x, self.pos_y = pos  # 20, 10

        self.start = pygame.transform.scale2x(load_image(start))
        self.middle = pygame.transform.scale2x(load_image(middle))
        self.end = pygame.transform.scale2x(load_image(end))
        self.bar_color = bar_color
        self.bar_rect_top_left = bar_rect_top_left
        self.max_bar_width = max_bar_width
        self.bar_height = bar_height

        # BG
        self.bar_bg = bar_bg
        self.start_bg = pygame.transform.scale2x(load_image(self.bar_bg[0]))
        self.middle_bg = pygame.transform.scale2x(load_image(self.bar_bg[1]))
        self.end_bg = pygame.transform.scale2x(load_image(self.bar_bg[2]))

    def background_bar(self, surface):
        # Bar bg
        if self.bar_bg is not None:
            surface.blits([
                [self.start_bg, (self.pos_x, self.pos_y)],
                [self.middle_bg, (self.pos_x + self.start.get_size()[0], self.pos_y)],
                [self.end_bg, (self.pos_x + self.start.get_size()[0] + self.middle.get_size()[0], self.pos_y)]
            ], doreturn=False)

    def draw_bar(self, surface):
        # Bar
        surface.blits([
            [self.start, (self.pos_x, self.pos_y)],
            [self.middle, (self.pos_x + self.start.get_size()[0], self.pos_y)],
            [self.end, (self.pos_x + self.start.get_size()[0] + self.middle.get_size()[0], self.pos_y)]
        ], doreturn=False)

    def bar(self, surface, current: float, full: float):
        current_ratio = current / full
        current_bar_width = self.max_bar_width * current_ratio
        pygame.draw.rect(surface, self.bar_color,
                         pygame.Rect(self.bar_rect_top_left, (current_bar_width, self.bar_height)))

    def show_bar(self, surface, current: float, full: float):
        self.background_bar(surface)
        self.bar(surface, current, full)
        self.draw_bar(surface)

    def get_length(self) -> int:
        return self.start.get_size()[0] + self.middle.get_size()[0] + self.end.get_size()[0]

    def get_size(self) -> tuple:
        """Returns tuple (width, height)"""
        return self.get_length() + self.pos_x * 2, self.start.get_size()[1]

    def get_width(self) -> float:
        return self.get_size()[0]

    def get_height(self) -> float:
        return self.get_size()[1]


# All skills
class UI(pygame.sprite.Sprite):
    def __init__(self, pos: Union[list, tuple]):
        super().__init__(all_group)
        self.image = pygame.Surface((252, 154), pygame.SRCALPHA)  # Transparent
        self.image.convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)

        bar_bg = [f'images/bar/background/bar_start.png',
                  f'images/bar/background/bar_middle.png',
                  f'images/bar/background/bar_end.png']

        # HP bar
        self.HpBar = GuiBar('images/bar/hp_bar_start.png', 'images/bar/bar_middle.png', 'images/bar/bar_end.png',
                            '#B02351', [52, 14], 187, 16, [0, 0], bar_bg)
        # Shield bar
        self.ShieldBar = GuiBar('images/bar/shield_bar_start.png', 'images/bar/bar_middle.png',
                                'images/bar/bar_end.png', '#CAA034',
                                [self.HpBar.bar_rect_top_left[0], self.HpBar.bar_rect_top_left[1]+52], 187, 16,
                                [0, self.HpBar.pos_y+self.HpBar.get_height()+2], bar_bg)
        # Superpower bar
        self.SuperpowerBar = GuiBar('images/bar/superpower_bar_start.png', 'images/bar/bar_middle.png',
                                    'images/bar/bar_end.png', '#16A436',
                                    [self.ShieldBar.bar_rect_top_left[0], self.ShieldBar.bar_rect_top_left[1] + 52],
                                    187, 16, [0, self.ShieldBar.pos_y + self.ShieldBar.get_height() + 2], bar_bg)

    def show_bars(self, player):
        self.HpBar.show_bar(self.image, player.hp, player.max_hp)
        self.ShieldBar.show_bar(self.image, player.shield_power, player.max_shield)
        self.SuperpowerBar.show_bar(self.image, player.super_power, player.max_super)

    def update(self, **kwargs):
        self.show_bars(kwargs.get('player'))


# Basic button
class Button(pygame.sprite.Sprite):
    def __init__(self, font, text, width, height, pos, elevation):
        super(Button, self).__init__(all_group)
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        self.image.convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)

        # Core attributes
        self.font = font
        self.pressed = False
        self.elevation = elevation
        self.dynamic_elevation = elevation
        self.original_y_pos = 5

        # top rectangle
        self.top_rect = pygame.Rect((0, 5), (width, height))
        self.top_color = '#475F77'

        # bottom rectangle
        self.bottom_rect = pygame.Rect((0, 5), (width, height))
        self.bottom_color = '#354B5E'
        # text
        self.text_surf = self.font.render(text, True, '#FFFFFF')
        self.text_rect = self.text_surf.get_rect(bottomright=self.top_rect.bottomright)

    def draw(self):
        # elevation logic
        self.top_rect.y = self.original_y_pos - self.dynamic_elevation
        self.text_rect.center = self.top_rect.center

        self.bottom_rect.midtop = self.top_rect.midtop
        self.bottom_rect.height = self.top_rect.height + self.dynamic_elevation

        pygame.draw.rect(self.image, self.bottom_color, self.bottom_rect, border_radius=12)
        pygame.draw.rect(self.image, self.top_color, self.top_rect, border_radius=12)

        self.image.blit(self.text_surf, self.text_rect)
        self.check_click()

    def check_click(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self.top_color = '#D74B4B'
            if pygame.mouse.get_pressed(3)[0]:
                self.dynamic_elevation = 0
                self.pressed = True
            else:
                self.dynamic_elevation = self.elevation
                if self.pressed:
                    self.action()
                    self.pressed = False
        else:
            self.dynamic_elevation = self.elevation
            self.top_color = '#475F77'

    def action(self):
        pass


# Level button
class LevelButton(Button):
    def __init__(self, load_level, level, font, text, width, height, pos, elevation):
        super().__init__(font, text, width, height, pos, elevation)
        self.level = level
        self.load_level = load_level

    def action(self):
        if self.pressed and self.level.unlocked:
            clear()
            self.load_level('game', self.level)


# Graphical levels list - choose level
class LevelMenu(list):
    def __init__(self, surface, font, level_list, load_level):
        super().__init__()
        self.surface = surface

        clear()
        pygame.mixer.stop()
        pygame.mouse.set_visible(True)

        self.background_image = load_image('images/background0.png')
        self.surface.blit(self.background_image, (0, 0))

        Image(ImageMod.upscale(load_image('images/title.png'), 3), screen_width/2, 50)  # Title image
        Title('Programista: Mateusz Kupis', 10, self.surface.get_height()-40)
        Title('Grafik: Zuzanna Stępień', 275, self.surface.get_height()-40)

        sound = load_sound(choice(['sound/bg0.wav', 'sound/bg1.wav', 'sound/bg2.wav']))
        sound.set_volume(.6)
        sound.play(-1)

        column = 1
        row = 4  # 1
        in_row = screen_width//192

        for level in level_list:
            if column > in_row:
                column, row = 1, row+1
            pos = 165 * column, 100 * row
            self.append(LevelButton(load_level, level, font, str(level.level_number), 50, 45, pos, 6))
            column += 1

    def draw(self):
        for level in self:
            if level.level.unlocked:
                level.draw()

    def run(self):
        all_group.clear(self.surface, self.background_image)
        all_group.update()

        dirty = all_group.draw(self.surface)
        pygame.display.update(dirty)

        self.draw()
