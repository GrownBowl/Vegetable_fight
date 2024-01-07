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

    def jump(self):
        self.y_vel = -self.gravity * 8

        self.animation_count = 0
        self.jump_count += 1

        if self.jump_count == 1:
            self.fall_count = 0

    def get_position(self):
        return self.rect.x, self.rect.y

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.gravity)
        self.move(self.x_vel, self.y_vel)
        self.fall_count += 1
        self.update_sprite()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, screen, offset_x):
        screen.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.y_vel < 0:
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
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1


class Tomato(pygame.sprite.Sprite):
    animation_delay = 4

    def __init__(self, x, y, width, height, direction, sprites):
        super().__init__()
        self.dead = False
        self.sprites = sprites
        self.rect = pygame.Rect(x, y, width, height)
        self.direction = direction
        self.animation_count = 0
        self.sprite = None
        self.mask = None
        self.update_sprite()

    def hit(self):
        self.dead = True

    def update_sprite(self):
        sprite_sheet_name = "idle" + "_" + self.direction
        sprites = self.sprites[sprite_sheet_name]
        sprite_index = (self.animation_count // self.animation_delay) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, screen, offset_x):
        screen.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))
