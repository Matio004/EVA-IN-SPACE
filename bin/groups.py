import pygame

# Groups
enemy_group = pygame.sprite.Group()  # Enemies
bullet_group = pygame.sprite.Group()  # Player bullets
enemy_bullet_group = pygame.sprite.Group()  # Enemy bullets
boss_bullet_group = pygame.sprite.Group()  # Boss bullets
shield_group = pygame.sprite.GroupSingle(None)  # Player shield
boss_group = pygame.sprite.GroupSingle(None)  # Boss
boss_shield_group = pygame.sprite.GroupSingle(None)  # Boss shield
ult_group = pygame.sprite.GroupSingle(None)  # Player ult group
all_group = pygame.sprite.RenderUpdates()  # Draw

containers = [enemy_group, bullet_group, enemy_bullet_group, boss_bullet_group, shield_group,
              boss_group, boss_shield_group, ult_group, all_group]


def clear():
    """Clear sprite group"""
    for group in containers:
        group.empty()
