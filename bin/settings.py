import pygame
import os

pygame.init()
screen_width, screen_height = pygame.display.get_desktop_sizes()[0]  # 1920, 1080
screen_height -= 60  # 60
screen_rect = pygame.Rect(0, 0, screen_width, screen_height)
# Binds
try:
    shot = 'space'.lower()  # Here write shot key name
    shield = 's'.lower()  # Here write shield key name
    super_power = 'f'.lower()  # Here write super power key name
    shot_key = pygame.key.key_code(shot)  # Shot key
    shield_key = pygame.key.key_code(shield)  # Shield key
    super_power_key = pygame.key.key_code(super_power)  # Super power key
    if not os.path.exists('./README.txt'):
        with open('./README.txt', 'w') as f:
            f.write(f'Tutorial\n'
                    f'Shot - {shot.upper()} or mouse button\nShield - {shield.upper()}\n'
                    f'Super - {super_power.upper()}\nMove - mouse\nF11 - full screen')

except ValueError:
    shot = 'space'.lower()
    shield = 's'.lower()
    super_power = 'f'.lower()
    shot_key = pygame.key.key_code(shot)  # Shot key
    shield_key = pygame.key.key_code(shield)  # Shield key
    super_power_key = pygame.key.key_code(super_power)  # Super power key
    with open('./crash_report.txt', 'w') as f:
        f.write('You entered bad key name. Check site https://www.pygame.org/docs/ref/key.html')
pygame.quit()
