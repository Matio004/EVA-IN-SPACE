from random import randint, choice, choices
from time import time

import pygame

# Own module
from pygame.math import Vector2

from .settings import screen_width, screen_height, screen_rect
from .groups import enemy_group, enemy_bullet_group, boss_bullet_group, boss_group,\
    boss_shield_group, all_group
from .files import load_images, load_image
from .images_modification import PlayerImages, BossImages, EngineImages


# Bonus
class Bonus(pygame.sprite.Sprite):
    bonus_count: int = 0
    is_running = False
    containers = all_group,

    def __init__(self, modifier: int, statistic: str, duration: float, image, player, game):
        super().__init__(*self.containers)
        self.image = pygame.transform.scale2x(image)  # self.frames[0][0] (100, 100)
        self.old_image = self.image.copy()
        self.rect = self.image.get_rect(center=(screen_width - 100, 100))

        # Own attributes
        Bonus.bonus_count += 1
        self.player = player
        self.game = game
        self.modifier = modifier
        self.statistic = statistic.split('.')[-1]
        self.time = time()
        self.duration = duration
        self.old_value = eval(statistic)

        # Animation
        self.particle = Particle(self, (224, 231, 237, 93), (3, 3))
        self.particles = 0
        self.particles_count = 5

    def animate(self):
        self.particle.draw((randint(0, self.rect.size[0]), randint(0, self.rect.size[1])))
        self.particles += 1

        if self.particles >= self.particles_count:
            self.particles = 0
            self.image = self.old_image.copy()

    def update(self, *args, **kwargs) -> None:
        self.animate()
        if self.statistic == 'kills':
            if not self.is_running:
                self.is_running = True
                self.game.kills += 5 * self.modifier
            if time() - self.time >= self.duration:
                self.kill()
                Bonus.bonus_count -= 1

        elif self.statistic == 'kill_bonus':
            if not self.is_running:
                self.is_running = True
                self.game.kill_bonus *= self.modifier
            if time() - self.time >= self.duration:
                self.game.kill_bonus //= self.modifier
                self.kill()
                Bonus.bonus_count -= 1

        elif self.statistic == 'max_bullet':
            if not self.is_running:
                self.is_running = True
                self.player.max_bullet *= self.modifier
            if time() - self.time >= self.duration:
                self.player.max_bullet //= self.modifier
                self.kill()
                Bonus.bonus_count -= 1


# Engines
class Engine(pygame.sprite.Sprite):
    frame_index = 0
    animation_speed: float = 16  # .45
    containers = all_group,

    def __init__(self, actor, x: float, y: float):
        super().__init__(*self.containers)
        self.x, self.y = x, y
        self.actor = actor
        self.frames = EngineImages(load_images('images/fire'), -90) if type(actor) == Player \
            else EngineImages(load_images('images/fire'), 90)
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(self.actor.rect.x - self.x, self.actor.rect.centery - self.y))

    def update(self, *args, **kwargs) -> None:
        self.animate(kwargs.get('dt'))

        if not self.actor.alive():
            self.kill()

        self.rect.center = self.actor.rect.x - self.x, self.actor.rect.centery - self.y

    def animate(self, dt):
        # Index error
        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        self.image = self.frames[int(self.frame_index)]  # change image
        self.frame_index += self.animation_speed*dt  # next image


# Player
class Player(pygame.sprite.Sprite):
    bullet_speed = 700  # 600  # 15
    super_speed = 400
    super_size = 4
    max_hp = 100
    hp = max_hp  # 100

    reloading = True

    # Shield
    max_shield = 15
    max_super = 40
    shield_power = max_shield
    super_power = max_super

    # Bullet
    max_bullet = 5

    # Pygame
    containers = all_group,

    def __init__(self):
        super().__init__(*self.containers)
        self.frames = PlayerImages(load_images('images/player'))
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(150, screen_height / 2))

        # Others
        self.bullet_image = pygame.transform.rotate(load_image('images/bullet/bullet1.png'), -90)

    def move(self, direction):
        self.rect.center = 150, direction

    def create_bullet(self, containers):
        return Bullet(2, self.bullet_image, self.rect.center[0], self.rect.center[1], self.bullet_speed, containers)

    def create_shield(self, containers):
        return Shield(self, containers)

    def create_superpower(self, containers):
        return Superpower(self.super_size, self.rect.x, self.rect.y, self.super_speed, containers)

    # Check powers
    def check_powers(self):
        if self.shield_power > self.max_shield:
            self.shield_power = self.max_shield
        if self.super_power > self.max_super:
            self.super_power = self.max_super

    def update(self, *args, **kwargs) -> None:
        # Move
        direction = pygame.mouse.get_pos()[1]
        self.move(direction)

        # Change image
        shield_percentage = self.shield_power / self.max_shield * 100
        if shield_percentage < 20:
            self.image = self.frames[0]
        elif 40 > shield_percentage >= 20:
            self.image = self.frames[1]
        elif 60 > shield_percentage >= 40:
            self.image = self.frames[2]
        elif 100 > shield_percentage >= 60:
            self.image = self.frames[3]
        elif shield_percentage == 100:
            self.image = self.frames[4]


# Bullets
class Bullet(pygame.sprite.Sprite):
    def __init__(self, size: int, image, pos_x: float, pos_y: float, direction: float, containers):
        super().__init__(*containers)
        self.image = pygame.transform.scale(image, (image.get_size()[0] * size, image.get_size()[1] * size))
        self.rect = self.image.get_rect(center=(pos_x, pos_y))

        self.direction = direction

        self.pos = Vector2(self.rect.center)

    def update(self, *args, **kwargs) -> None:
        dt = kwargs.get('dt')

        self.pos.x += self.direction*dt

        self.rect[0] = round(self.pos.x)  #+= self.direction
        if self.rect[0] >= screen_width and self.direction > 0:
            self.kill()
        if self.rect[0] <= 0 and self.direction < 0:
            self.kill()


# Shield
class Shield(pygame.sprite.Sprite):
    hp = 100

    frame_index = 0
    animation_speed: float = 16

    def __init__(self, sprite, containers):
        super().__init__(*containers)
        self.sprite = sprite

        size = max(self.sprite.rect.size[0], self.sprite.rect.size[1]) * 2
        shield_size = size, size

        self.frames = [pygame.transform.scale(load_image('images/shield.png') if type(self.sprite) == Player
                                              else load_image('images/boss_shield.png'), shield_size)]
        self.frames.extend([
            pygame.transform.flip(self.frames[0], True, False),
            pygame.transform.flip(self.frames[0], True, True),
            pygame.transform.flip(self.frames[0], False, True)
                            ])

        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=self.sprite.rect.center)

        self.default_hp = self.hp

    def update(self, *args, **kwargs) -> None:
        if not self.sprite.alive():
            self.kill()
        self.rect.center = self.sprite.rect.center

        self.animate(kwargs.get('dt'))

    def animate(self, dt):
        # Index error
        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        self.image = self.frames[int(self.frame_index)]  # change image
        self.frame_index += self.animation_speed * dt  # next image


# Enemy
class Enemy(pygame.sprite.Sprite):
    # Presets
    speed = 80
    forward = 4000
    bullet_speed = -320  # -8
    hp = 2
    facing = choice((-1, 1))
    max_bullet = 7  # 7
    has_bullet = False

    # Bullet
    bullet: Bullet
    bullet_groups = all_group, enemy_bullet_group

    # Pygame
    containers = all_group, enemy_group

    def __init__(self, pos_x: float, pos_y: float, image):
        super().__init__(*self.containers)
        self.image = image
        self.rect = self.image.get_rect(center=(pos_x, pos_y))

        # Others
        self.bullet_image = pygame.transform.rotate(load_image('images/bullet/bullet0.png'), 90)

        self.pos = Vector2(self.rect.center)

    def update(self, *args, **kwargs) -> None:
        dt = kwargs.get('dt')

        self.bullet_generator()

        self.pos.y += self.facing * self.speed * dt
        self.rect.y = round(self.pos.y)

        if not screen_rect.contains(self):
            self.pos.x = self.rect.x - self.forward * dt
            self.rect.x = round(self.pos.x)

            self.facing = -self.facing

            self.pos.y += self.facing * self.speed * dt
            self.rect.y = round(self.pos.y)

        if self.rect.centerx <= 0:
            self.rect.centerx = randint(600, screen_width - 100)

    def create_bullet(self, bullet_image, containers):
        return Bullet(3, bullet_image, self.rect.center[0], self.rect.center[1], self.bullet_speed, containers)  # 3

    def bullet_generator(self):
        if len(enemy_bullet_group) <= self.max_bullet and not self.has_bullet and\
                choices([True, False], weights=[80, 20], k=1)[0]:  # Shot probability .8 possible if self has only one b
            self.bullet = self.create_bullet(self.bullet_image, self.bullet_groups)
            self.has_bullet = True

        # Reset bullet counter
        if self.has_bullet:
            if not self.bullet.alive():
                self.has_bullet = False


# Boss
class Boss(pygame.sprite.Sprite):
    # Presets
    facing = choice((-1, 1))
    speed = 80
    forward = 4000
    bullet_speed = -400  # -10
    hp = 2

    # Shield
    max_shield = 15
    shield_power = max_shield

    # Bullet
    bullet_groups = all_group, boss_bullet_group

    # Pygame
    containers = all_group, boss_group

    def __init__(self, pos_x: float, pos_y: float):
        super().__init__(*self.containers)
        self.frames = BossImages(load_images('images/boss'))
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(pos_x, pos_y))

        # Others
        self.bullet_image = pygame.transform.rotate(load_image('images/bullet/bullet0.png'), 90)

        self.pos = Vector2(self.rect.center)

    def update(self, *args, **kwargs) -> None:
        dt = kwargs.get('dt')

        self.bullet_generator()
        # Move
        self.pos.y += self.facing * self.speed * dt
        self.rect.y = round(self.pos.y)

        if not screen_rect.contains(self):
            self.pos.x = self.rect.x - self.forward * dt
            self.rect.x = round(self.pos.x)

            self.facing = -self.facing

            self.pos.y += self.facing * self.speed * dt
            self.rect.y = round(self.pos.y)

        if self.rect.centerx <= 0:
            self.rect.centerx = randint(600, screen_width - 100)

        # picture
        shield_percentage = self.shield_power / self.max_shield * 100
        if shield_percentage < 20:
            self.image = self.frames[0]
        elif 40 > shield_percentage >= 20:
            self.image = self.frames[1]
        elif 60 > shield_percentage >= 40:
            self.image = self.frames[2]
        elif 100 > shield_percentage >= 60:
            self.image = self.frames[3]
        elif shield_percentage == 100:
            self.image = self.frames[4]

        # Boss powers increase
        if self.shield_power < self.max_shield and len(boss_shield_group) == 0:
            self.shield_power += 2 * dt

        # Check powers
        if self.shield_power > self.max_shield:
            self.shield_power = self.max_shield

    def create_bullet(self, bullet_image, containers):
        return Bullet(3, bullet_image, self.rect.center[0], self.rect.center[1], self.bullet_speed, containers)  # 3

    def create_shield(self, containers):
        return Shield(self, containers)

    def bullet_generator(self):
        if len(boss_bullet_group) < 1:
            self.create_bullet(self.bullet_image, self.bullet_groups)


# Explosion
class Boom(pygame.sprite.Sprite):
    # Attributes
    default_life = 12
    animation_frames = 3
    animation_speed = 21  # .6
    # Pygame
    containers = all_group,

    def __init__(self, actor, frames):
        super().__init__(*self.containers)

        size = max(actor.rect.size)
        self.frames = [pygame.transform.scale(image, (size, size)) for image in frames]

        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=actor.rect.center)

    def update(self, *args, **kwargs) -> None:
        self.default_life -= self.animation_speed*kwargs.get('dt')
        self.image = self.frames[int(self.default_life) // self.animation_frames % 2]
        if self.default_life <= 0:
            self.kill()


# Superpower
class Superpower(pygame.sprite.Sprite):
    frame_index = 0
    animation_speed: float = 11  # .3

    def __init__(self, size: int, pos_x: float, pos_y: float, speed: float, containers):
        super().__init__(*containers)

        self.frames = [pygame.transform.scale(image, (image.get_size()[0] * size, image.get_size()[1] * size))
                       for image in [load_image('images/wave.png'),
                                     pygame.transform.flip(load_image('images/wave.png'), False, True)]]
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(pos_x, pos_y))

        self.speed = speed

        self.pos = Vector2(self.rect.center)

    def update(self, *args, **kwargs) -> None:
        dt = kwargs.get('dt')

        self.animate(dt)

        self.pos.x += self.speed * dt
        self.rect.x = round(self.pos.x)

        if self.rect.centerx > screen_width:
            self.kill()

    def animate(self, dt):
        # Index error
        if self.frame_index > len(self.frames):
            self.frame_index = 0

        self.image = self.frames[int(self.frame_index)]  # Change image
        self.frame_index += self.animation_speed * dt  # Next image


# Score
class Score(pygame.sprite.Sprite):
    containers = all_group,

    def __init__(self, pos_x: float, pos_y: float, game):
        super().__init__(*self.containers)
        self.game = game
        self.font = pygame.font.Font('font/Roboto-Medium.ttf', 32)
        self.color = pygame.Color(255, 255, 255)
        self.update()
        self.rect = self.image.get_rect().move(pos_x, pos_y)

    def update(self, *args, **kwargs) -> None:
        """Current level and kills"""
        msg = '{} | Kills: {:d} | Boss on: {}'.\
            format(self.game.level, self.game.kills,
                   self.game.boss_kills_value if self.game.kills != self.game.level.kills
                   else self.game.boss_kills_value - self.game.boss_kills_bonus_value)

        self.image = self.font.render(msg, True, self.color)


# Particle
class Particle:
    def __init__(self, actor, color, size):
        # Core
        self.actor = actor
        self.color = color
        self.size = size
        self.surface = pygame.Surface(size, pygame.SRCALPHA).convert_alpha()

        self.create_particle()

    def draw(self, pos):
        self.actor.image.blit(self.surface, pos)

    def create_particle(self):
        pygame.draw.rect(self.surface, self.color, pygame.Rect((0, 0), self.size))


# Title
class Title(pygame.sprite.Sprite):
    containers = all_group,

    def __init__(self, text, pos_x, pos_y):
        super().__init__(*self.containers)
        self.font = pygame.font.Font('font/Roboto-Medium.ttf', 20)
        self.color = pygame.Color(209, 227, 232)

        self.image = self.font.render(text, True, self.color)
        self.rect = self.image.get_rect(topleft=(pos_x, pos_y))


class Image(pygame.sprite.Sprite):
    containers = all_group,

    def __init__(self, image, pos_x, pos_y):
        super().__init__(*self.containers)
        self.image = image
        self.rect = self.image.get_rect(midtop=(pos_x, pos_y))

