# Python Lib
from random import randint, choice, choices

# Modules
from time import time

from . import settings
from .files import load_image, load_sound, load_images, save_levels, load_saves
from .groups import enemy_group, bullet_group, enemy_bullet_group, boss_bullet_group, shield_group, boss_group, \
    boss_shield_group, ult_group, all_group, clear
from .gui import UI
from .images_modification import EnemyImages
from .levels import LevelData
from .settings import screen_width, screen_height
from .sprites import Bonus, Engine, Player, Bullet, Shield, Enemy, Boss, Boom, Superpower, Score

# Pygame
try:
    import pygame
except ImportError:
    with open('../crash_report.txt', 'w') as f:
        f.write('At first install pygame lib. Write \'pip install pygame\' in cmd.')
    raise ImportError('At first install pygame lib. Write \'pip install pygame\' in cmd.')

boss_value = 50
# Levels
levels_list = load_saves(10)  # 10
save_levels(levels_list)


# Generate Bonus
def random_bonus(chance: float, bonus_images, player, game):
    if choices([True, False], weights=[chance, 100 - chance], k=1)[0] and Bonus.bonus_count < 1:
        bonus = choices(['self.game.kills', 'self.game.kill_bonus', 'self.player.max_bullet'],
                        weights=[.25, .25, .5], k=1)[0]
        return Bonus(2, bonus, 10, bonus_images[bonus.split('.')[-1]], player, game)
    return None


# Main
class Game:
    # Player
    player: Player
    shield: Shield
    ult: Superpower

    # Stats
    ui: UI

    # Presets
    kill_bonus = 1
    kills = 0

    # Boss presets
    boss: Boss
    boss_shield: Shield
    boss_kills_bonus_value = 50
    # Boss not exists
    boss_exists = False
    # Boss not killed
    boss_killed = False

    # Enemy presets
    max_enemy = 10  # 10

    def __init__(self, master, level: LevelData, boss_kills_value: int = 50):
        self.level = level
        self.boss_kills_value = boss_kills_value
        self.master = master

        clear()  # clear sprite group

        # Screen
        self.screen = self.master.screen
        self.background_image = pygame.transform.scale(load_image(f'images/bg{choice(range(0, 5))}.png'),
                                                       self.screen.get_size())
        # Images
        # Boom
        boom_images = [[load_image('images/boom0.png')], [load_image('images/boom2.png')]]
        self.ship_boom_images = [boom_images[0][0], pygame.transform.flip(boom_images[0][0], True, True)]
        self.bullet_boom_images = [boom_images[1][0], pygame.transform.flip(boom_images[1][0], True, True)]

        # Enemy
        self.enemy_images = EnemyImages(list(load_images('images/enemy')))

        # Bonus
        self.bonus_images = {'kills': load_image('images/modifiers/kills_modifier.png'),
                             'kill_bonus': load_image('images/modifiers/kill_bonus_modifier.png'),
                             'max_bullet': load_image('images/modifiers/max_bullet_modifier.png')}

        # Channels
        main_volume = .75  # Main channel
        self.effects_channel = pygame.mixer.Channel(0)  # Effects channel
        self.shot_channel = pygame.mixer.Channel(1)  # Shot channel
        self.explosion_channel = pygame.mixer.Channel(2)  # Explosion channel
        self.music_channel = pygame.mixer.Channel(3)  # BG music channel
        # Volume
        self.effects_channel.set_volume(main_volume * .4)  # effects volume
        self.shot_channel.set_volume(main_volume * .2)  # shot volume
        self.explosion_channel.set_volume(main_volume * .4)  # explosion volume
        self.music_channel.set_volume(main_volume * .8)  # music volume

        # Sounds
        # BG soundtrack
        background = [load_sound('sound/bg0.wav'), load_sound('sound/bg1.wav'), load_sound('sound/bg2.wav')]
        self.blast_sound = load_sound('sound/Laser_Blasts.wav')  # Blast
        self.super_sound = load_sound('sound/Laser_Cannon.wav')  # Super
        self.shield_on = load_sound('sound/shooting_star.wav')  # Shield on
        self.shield_break = load_sound('sound/shield_break1.wav')  # Shield off
        # Shield -hp
        _hp_shield = [load_sound('sound/shield-hp0.wav'), load_sound('sound/shield-hp1.wav'),
                      load_sound('sound/bullet-bullet.wav')]
        self._hp_player = [load_sound('sound/player-hp0.wav'), load_sound('sound/player-hp1.wav')]  # Player -hp
        self.bullet_bullet_sound = load_sound('sound/bullet-bullet.wav')  # Bullets collision
        self.boom = [load_sound('sound/boom0.wav'), load_sound('sound/boom1.wav'),
                     load_sound('sound/boom2.wav')]  # Explosion

        # Bg music
        if pygame.mixer:
            self.music_channel.play(choice(background), -1)

        pygame.mouse.set_visible(False)
        # Player group
        self.ui = UI((5, 5))
        self.player = Player()

        # Scoreboard
        Score(self.ui.image.get_width()+8, 5, self)

        # Player engine
        Engine(self.player, 12, 10), Engine(self.player, 12, -10)

        # Background
        self.screen.blit(self.background_image, (0, 0))

        self.prev_time = time()

    def check_collisions(self):
        # Collisions
        # Collide enemy - player bullet
        for _enemy in pygame.sprite.groupcollide(enemy_group, bullet_group, True, True):
            self.kills += 1
            if self.player.super_power < self.player.max_super:
                self.player.super_power += self.kill_bonus
            if self.player.shield_power < self.player.max_shield:
                self.player.shield_power += self.kill_bonus

            random_bonus(10, self.bonus_images, self.player, self)  # Generate Bonus

            # Play sound
            if pygame.mixer:
                self.explosion_channel.play(choice(self.boom), 0)
            Boom(_enemy, self.ship_boom_images)

        # player_bullet/player_shield/player - enemy_bullet or boss_bullet
        for group in [enemy_bullet_group, boss_bullet_group]:
            # Collide player bullet - others_bullet
            for _bullet in pygame.sprite.groupcollide(bullet_group, group, True, True):
                if self.player.super_power < self.player.max_super:
                    self.player.super_power += self.kill_bonus / 2
                if self.player.shield_power < self.player.max_shield:
                    self.player.shield_power += self.kill_bonus / 2
                Boom(_bullet, self.bullet_boom_images)

                # Play sound
                if pygame.mixer:
                    self.effects_channel.play(self.bullet_bullet_sound, 0)

            # Shield - enemy/boss_bullet
            if len(shield_group) == 1:
                for _enemy_bullet in pygame.sprite.spritecollide(self.shield, group, True):
                    # Play sound
                    if pygame.mixer:
                        self.effects_channel.play(choice(self._hp_player), 0)
                    self.shield.hp -= 10
                    if self.player.hp < self.player.max_hp:
                        self.player.hp += self.kill_bonus
                    # Kill
                    if self.shield.hp <= 0:
                        self.shield.kill()
                        # Boss shield += 1
                        if self.boss_exists:
                            if self.boss.shield_power < self.boss.max_shield:
                                self.boss.shield_power += self.kill_bonus
                        # Play sound
                        if pygame.mixer:
                            self.effects_channel.play(self.shield_break, 0)
            else:
                # Collide player - enemy/boss bullet
                for _enemy_bullet in pygame.sprite.spritecollide(self.player, group, True):
                    # Kill
                    if self.player.hp <= 0:
                        self.player.kill()
                        Boom(self.player, self.ship_boom_images)

                    if _enemy_bullet in boss_bullet_group:
                        # Boss shield += 1
                        if self.boss.shield_power < self.boss.max_shield:
                            self.boss.shield_power += self.kill_bonus / 2

                    # Play sound
                    if pygame.mixer:
                        self.effects_channel.play(choice(self._hp_player), 0)
                    self.player.hp -= 10

        # Collide shield - enemy
        '''Tarcza chroni przed pociskami a nie przeciwnikami'''

        # Collide player - enemy or boss
        for enemy_or_boss in [enemy_group, boss_group]:
            for _enemy in pygame.sprite.spritecollide(self.player, enemy_or_boss, True):
                # Play sound
                if pygame.mixer:
                    self.explosion_channel.play(choice(self.boom), 0)
                self.player.hp = 0
                self.player.kill()
                Boom(_enemy, self.ship_boom_images)

        # Super - boss, enemy, bullets
        if len(ult_group):
            for _group in [boss_shield_group, boss_group, enemy_group,
                           boss_bullet_group, enemy_bullet_group]:
                for _entity in pygame.sprite.spritecollide(self.ult, _group, False):
                    if _entity in boss_shield_group:
                        _entity.kill()
                        self.ult.kill()
                        # Play sound
                        if pygame.mixer:
                            self.effects_channel.play(self.shield_break, 0)
                    if type(_entity) == Enemy and _entity not in boss_group:
                        self.kills += 1
                        # Play sound
                        if pygame.mixer:
                            self.explosion_channel.play(choice(self.boom), 0)

                        self.player.shield_power += self.kill_bonus
                        _entity.kill()
                        Boom(_entity, self.ship_boom_images)
                    if type(_entity) == Bullet:
                        # Play sound
                        if pygame.mixer:
                            self.explosion_channel.play(self.bullet_bullet_sound, 0)

                        _entity.kill()
                        self.player.shield_power += self.kill_bonus / 2
                        Boom(_entity, self.bullet_boom_images)
                    if _entity in boss_group:
                        self.ult.kill()
                        self.boss.hp -= 100

        # Boss Shield - player bullet
        if len(boss_shield_group) == 1:
            for _player_bullet in pygame.sprite.spritecollide(self.boss_shield, bullet_group, True):
                # Play sound
                if pygame.mixer:
                    self.effects_channel.play(choice(self._hp_player), 0)
                self.boss_shield.hp -= 10
                if self.boss.hp < 100:
                    self.boss.hp += self.kill_bonus
                # Kill
                if self.boss_shield.hp <= 0:
                    self.boss_shield.kill()
                    # Play sound
                    if pygame.mixer:
                        self.effects_channel.play(self.shield_break, 0)

        # Collide player_bullet - boss
        # Boss update
        elif len(boss_group):
            if self.boss.hp <= 0:
                if self.boss_kills_value <= self.level.kills:
                    self.boss_killed = False
                else:
                    self.boss_killed = True
                self.kills += self.kill_bonus
                self.boss.kill()
                Boom(self.boss, self.ship_boom_images)
                # Play sound
                if pygame.mixer:
                    self.explosion_channel.play(choice(self.boom), 0)
                self.boss_exists = not self.boss_exists
            for _bullet in pygame.sprite.spritecollide(self.boss, bullet_group, True):
                self.boss.hp -= 10
                Boom(_bullet, self.bullet_boom_images)

    # Enemy generator
    def generate_enemies(self):
        if len(enemy_group) < self.max_enemy:
            x = randint(screen_width // 3, screen_width - 100)
            y = randint(100, screen_height - 100)
            Enemy(x, y, choice(self.enemy_images))
        return None

    def run(self):
        dt = time()-self.prev_time
        self.prev_time = time()

        # Game loop
        if self.player.hp > 0 and (self.kills < self.level.kills or not self.boss_killed):
            self.generate_enemies()  # Enemy generator

            # Boss spawn
            if self.kills >= self.boss_kills_value and not self.boss_exists:
                self.boss = Boss(screen_width / 2, screen_height / 2)
                self.boss.shield_power = self.boss.max_shield

                self.boss.hp *= self.boss_kills_value  # Set boss hp

                Engine(self.boss, -self.boss.rect.width - 12, 10)
                Engine(self.boss, -self.boss.rect.width - 12, -10)  # Boss engine

                self.boss_exists = not self.boss_exists
                self.boss_kills_value += self.boss_kills_bonus_value

            # Boss bullet generator and shield
            if len(boss_group) == 1:
                if self.boss.shield_power == self.boss.max_shield and not len(boss_shield_group) and \
                        choices([True, False], weights=[1, 99], k=1)[0]:  # Shield probability .1
                    self.boss.shield_power = 0
                    self.boss_shield = self.boss.create_shield([all_group, boss_shield_group])
                    # Play sound
                    if pygame.mixer:
                        self.effects_channel.play(self.shield_on, 0)

            # Key events
            key_get_pressed = pygame.key.get_pressed()
            # Create shield
            if key_get_pressed[settings.shield_key] and self.player.shield_power == self.player.max_shield \
                    and not len(shield_group):
                self.player.shield_power = 0
                self.shield = self.player.create_shield([all_group, shield_group])
                # Play sound
                if pygame.mixer:
                    self.effects_channel.play(self.shield_on, 0)
            # Super power
            if key_get_pressed[settings.super_power_key] and self.player.super_power == self.player.max_super:
                self.player.super_power = 0
                self.ult = self.player.create_superpower([all_group, ult_group])
                # Play sound
                if pygame.mixer:
                    self.effects_channel.play(self.super_sound, 0)

            # Shoot
            firing = key_get_pressed[settings.shot_key] or pygame.mouse.get_pressed(3)[0]
            if not self.player.reloading and firing and len(bullet_group) < self.player.max_bullet:
                self.player.create_bullet([all_group, bullet_group])
                # Play sound
                if pygame.mixer:
                    self.shot_channel.play(self.blast_sound, 0)
            self.player.reloading = firing

            # Collisions
            self.check_collisions()
            self.player.check_powers()

            # Draw all entities
            all_group.clear(self.screen, self.background_image)
            all_group.update(player=self.player, dt=dt)

            dirty = all_group.draw(self.screen)
            pygame.display.update(dirty)

        # If player no HP
        else:
            if len(levels_list) != self.level.level_number and self.player.hp > 0:
                levels_list[self.level.level_number].unlocked = True
            save_levels(levels_list)
            self.master.create_levels()
            self.master.state = 'level'
