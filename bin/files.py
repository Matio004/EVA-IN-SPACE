import pygame
import os
from .levels import LevelData, create_levels

# Dir
save_dir = os.path.join('bin', 'saves', 'level_save.txt')


# Image loader
def load_image(path):
    # loads an image, prepares it for play
    try:
        surface = pygame.image.load(path)
    except FileNotFoundError:
        surface = pygame.image.load('images/icon.png')
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s' % (path, pygame.get_error()))
    return surface.convert_alpha()


# Images from direction
def load_images(direction):
    files = [file for file in os.listdir(direction) if os.path.isfile(os.path.join(direction, file))]
    for file in files:
        try:
            surface = pygame.image.load(os.path.join(direction, file))
        except pygame.error:
            raise SystemExit('Could not load image "%s" %s' % (file, pygame.get_error()))
        yield surface.convert_alpha()


# Sound loader
def load_sound(path):
    if not pygame.mixer:
        return None
    try:
        sound = pygame.mixer.Sound(path)
        return sound
    except pygame.error:
        print("Warning, unable to load, %s" % path)
    return None


# Saver
def save(level: LevelData):
    with open(save_dir, 'w') as file:
        file.write(str(level.level_number - 1))


def save_levels(level_list):
    with open(save_dir, 'w') as file:
        for level in level_list:
            file.write(str(list(iter(level))).lstrip('[').rstrip(']'))
            file.write('\n')


def load_saves(count):
    level_list = []
    if os.path.exists(save_dir):
        with open(save_dir, 'r') as file:
            levels = file.readlines()
            levels = [level.split() for level in levels]
            levels = [[stat.strip(',') for stat in level] for level in levels]
            levels = [[int(level[0]), int(level[1]), 1 if level[2] == 'True' else 0] for level in levels]
            if len(levels) == count:
                for level_num, kills, unlocked in levels:
                    level_list.append(LevelData(int(level_num), int(kills), bool(unlocked)))
                return level_list
            else:
                return create_levels(count)
    else:
        return create_levels(count)


# Save loader
def load_save(levels_list) -> LevelData:
    if os.path.exists(save_dir):
        with open(save_dir, 'r') as file:
            try:
                return levels_list[int(file.read(-1))]
            except ValueError:
                return levels_list[0]
            except IndexError:
                return levels_list[-1]
    else:
        return levels_list[0]


# Del save
def del_save():
    return os.remove(save_dir)
