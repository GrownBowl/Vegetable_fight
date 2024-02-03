import pygame


# Родительский класс всех объектов
class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, screen, offset_x):
        """Метод отрисовки объекта"""

        screen.blit(self.image, (self.rect.x - offset_x, self.rect.y))


# Класс деревяшек
class WoodBlock(Object):
    def __init__(self, x, y, size, block):
        super().__init__(x, y, size, size)
        block = block
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


# Класс блока, двигающегося вверх вниз
class UpDownBlock(WoodBlock):
    def __init__(self, x, y, size, block, traveling_distance):
        super().__init__(x, y, size, block)
        self.first_y = y
        self.traveling_distance = traveling_distance
        self.direction = 1

    def update(self):
        """Обновление позиции объекта"""

        if self.first_y == self.rect.y:
            self.direction = -1
        elif self.rect.y == self.first_y - self.traveling_distance:
            self.direction = 1
        self.rect = self.rect.move(0, self.direction)


# Класс блока, двигающегося влево вправо
class LeftRightBlock(WoodBlock):
    def __init__(self, x, y, size, block, traveling_distance):
        super().__init__(x, y, size, block)
        self.first_x = x
        self.traveling_distance = traveling_distance
        self.direction = 1

    def update(self):
        """Обновление позиции объекта"""

        if self.first_x == self.rect.x:
            self.direction = 1
        elif self.rect.x == self.first_x + self.traveling_distance:
            self.direction = -1
        self.rect = self.rect.move(self.direction, 0)


# Класс шипов
class ThornsBlock(WoodBlock):
    pass


# Класс блока замедления
class SlowdownBlock(WoodBlock):
    pass


# Класс блока ускорения
class BoostBlock(WoodBlock):
    pass


# Класс капельки
class DropBlock(WoodBlock):
    def __init__(self, x, y, size, block, id):
        self.id = id
        super().__init__(x, y, size, block)

    def get_id(self):
        return self.id


class FinishBlock(WoodBlock):
    pass


class Hp(WoodBlock):
    pass
