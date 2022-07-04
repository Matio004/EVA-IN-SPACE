import pygame


class ImageMod:
    @staticmethod
    def upscale(image, scale):
        return pygame.transform.scale(image, (image.get_size()[0]*scale, image.get_size()[1]*scale))


class Images(list):
    def __new__(cls, *images):
        return super().__new__(cls, images)

    def upscale(self, scale: int):
        for image in self:
            self[self.index(image)] = pygame.transform.scale(image, [image.get_size()[0]*scale,
                                                                     image.get_size()[1]*scale])
        return self

    def rotate(self, angle: float):
        for image in self:
            self[self.index(image)] = pygame.transform.rotate(image, angle)
        return self

    def flip(self, x_bool: bool, y_bool: bool):
        for image in self:
            self[self.index(image)] = pygame.transform.flip(image, x_bool, y_bool)
        return self


class PlayerImages(Images):
    def __init__(self, images):
        super().__init__(images)
        self.upscale(2)
        self.rotate(-90)


class EnemyImages(Images):
    def __init__(self, images):
        super().__init__(images)
        self.upscale(2)
        self.rotate(90)


class BossImages(Images):
    def __init__(self, images):
        super().__init__(images)
        self.upscale(2)
        self.rotate(90)


class EngineImages(Images):
    def __init__(self, images, angle):
        super().__init__(images)
        self.upscale(3)
        self.rotate(angle)
