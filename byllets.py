import pygame


class HeroBullets(pygame.sprite.Sprite):
    def __init__(self, screen, hero, direction, offset_x, sprites):
        super().__init__()
        self.sprites = sprites
        self.offset_x = offset_x
        self.screen = screen
        self.rect = pygame.Rect(0, 0, 32, 32)
        self.speed = 10
        self.direction = direction
        self.rect.centerx = hero.rect.centerx
        self.rect.top = hero.rect.top
        self.sprite = self.sprites[f"potato_pellet_" + self.direction][0]
        self.mask = None

    def get_position_x(self):
        return self.rect.x

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def update(self):
        """Перемещение пули"""

        if self.direction == "left":
            self.rect.x -= self.speed
        else:
            self.rect.x += self.speed

        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, screen, offset_x):
        screen.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))
