import pygame


class Hero(pygame.sprite.Sprite):
    gravity = 1
    animation_delay = 4

    def __init__(self, x, y, width, height, sprites):
        super().__init__()
        self.sprites = sprites
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.sprite = None
        self.mask = None
        self.hp = 3
        self.hit = False
        self.hit_count = 0

    def get_hp(self):
        """Метод возвращающий количество хп"""

        return self.hp

    def jump(self):
        """Метод прыжка персонажа"""

        self.y_vel = -self.gravity * 8

        self.animation_count = 0
        self.jump_count += 1

        if self.jump_count == 1:
            self.fall_count = 0

    def get_position(self):
        """Метод возвращающий позицию пероснажа"""

        return self.rect.x, self.rect.y

    def move(self, dx, dy):
        """Метод передвежения персонажа"""

        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel):
        """Метод передвежения персонажа влево"""

        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        """Метод передвежения персонажа вправо"""

        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        """Главный цикл персонажа"""

        self.y_vel += min(1, (self.fall_count / fps) * self.gravity)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def update(self):
        """Метод обновления персонажа"""

        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, screen, offset_x):
        """Метод отрисовки персонажа"""

        screen.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

    def update_sprite(self):
        """Метод обновления анимаций"""

        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.gravity * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.sprites[sprite_sheet_name]
        sprite_index = (self.animation_count // self.animation_delay) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def landed(self):
        """Метод приземления персонажа"""

        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        """Метод столкновения персонажа головой об объект"""

        self.count = 0
        self.y_vel *= -1

    def die(self):
        """Метод смерти персонажа"""

        self.hp = 0


class Tomato(pygame.sprite.Sprite):
    animation_delay = 10

    def __init__(self, x, y, width, height, direction, sprites):
        super().__init__()
        self.sprites = sprites
        self.rect = pygame.Rect(x, y, width, height)
        self.direction = direction
        self.bullets = pygame.sprite.Group()
        self.animation_count = 0
        self.sprite = None
        self.mask = None
        self.dead = False
        self.update_sprite()

    def hit(self):
        """Метод получения урона"""

        self.dead = True

    def update_sprite(self):
        """Метод обновления анимаций"""

        sprite_sheet_name = "tomato" + "_" + self.direction
        sprites = self.sprites[sprite_sheet_name]
        sprite_index = (self.animation_count // self.animation_delay) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        """Метод обновления персонажа"""

        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, screen, offset_x):
        """Метод отрисовки персонажа"""

        screen.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))
