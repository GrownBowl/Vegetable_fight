import os
import sys
import pygame
from byllets import HeroBullets
from levels import create_first_level

pygame.init()
MAPS_DIR = "maps"
FPS = 60
size = WIDTH, HEIGHT = 1280, 720
hero_speed = 5

screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
hero_bullets = pygame.sprite.Group()


def draw_background(bck):
    """Функция отрисовки заднего фона"""

    screen.blit(bck, (0, 0))


def flip_image(sprites):
    """Функция отзеркаливания изображения"""

    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_block(size):
    """Функция загрузки блоков"""

    path = os.path.join("assets", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return surface


def load_sprite_sheets(directory, width, height, flip=False):
    """Функция загрузки отдельных кадров анимаций"""

    path = os.path.join("assets", directory)
    images = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    everyone_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(os.path.join(path, image)).convert_alpha()

        sprites_list = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites_list.append(pygame.transform.scale2x(surface))

        if flip:
            everyone_sprites[image.replace(".png", "") + "_right"] = sprites_list
            everyone_sprites[image.replace(".png", "") + "_left"] = flip_image(sprites_list)
        else:
            everyone_sprites[image.replace(".png", "")] = sprites_list

    return everyone_sprites


def draw(screen, hero, persons, objects, bullets, offset_x):
    """Функция отрисовки всего на экране"""

    # Отрисовываем объекты
    for obj in objects:
        obj.draw(screen, offset_x)

    # Отрисовываем пули
    for bullet in bullets.sprites():
        bullet.draw(screen, offset_x)

    # Отрисовываем персонажей
    for person in persons:
        person.draw(screen, offset_x)

    # Отрисовываем главного героя
    hero.draw(screen, offset_x)
    pygame.display.flip()


def vertical_collision(hero, objects, dy):
    """Функция проверки на вертикальное столковения. Возвращает все объекты, с которыми произошло столкновение"""

    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(hero, obj):
            if dy > 0:
                hero.rect.bottom = obj.rect.top
                hero.landed()
            elif dy < 0:
                hero.rect.top = obj.rect.bottom
                hero.hit_head()

        collided_objects.append(obj)

    return collided_objects


def collide(hero, objects, dx):
    hero.move(dx, 0)
    hero.update()
    collided_object = None

    for obj in objects:
        if pygame.sprite.collide_mask(hero, obj):
            collided_object = obj
            break

    hero.move(-dx, 0)
    hero.update()
    return collided_object


def bullets_update(bullets, objects, persons):
    """Обновление позиций пуль"""

    for bullet in bullets.copy():
        collide_person = collide(bullet, persons, bullet.speed)
        if collide_person:
            bullets.remove(bullet)
            collide_person.hit()

        if collide(bullet, objects, bullet.speed):
            bullets.remove(bullet)

        if bullet.get_position_x() > 3000 or bullet.get_position_x() < 0:
            bullets.remove(bullet)

    bullets.update()


def hero_move(hero, objects, persons):
    """Обновление героя, проверка на столкновения"""

    for person in persons:
        person.update_sprite()

    hero.loop(FPS)
    keys = pygame.key.get_pressed()

    hero.x_vel = 0
    collide_left = collide(hero, objects, -hero_speed * 2)
    collide_right = collide(hero, objects, hero_speed * 2)

    if keys[pygame.K_a] and not collide_left:
        hero.move_left(hero_speed)
    if keys[pygame.K_d] and not collide_right:
        hero.move_right(hero_speed)

    vertical_collision(hero, objects, hero.y_vel)


def main():
    bck = pygame.image.load("assets/Bez_imeni-2.png")
    running = True

    block_size = 48
    persons, objects = create_first_level(block_size, WIDTH, HEIGHT, load_block(block_size),
                                          load_sprite_sheets("hero", 32, 32, True),
                                          load_sprite_sheets("tomato", 32, 32, True))
    hero = persons.pop(0)

    offset_x = 0
    scroll_area_width = 200

    while running:
        draw_background(bck)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and hero.jump_count < 2:
                    hero.jump()

                if event.key == pygame.K_s:
                    new_hero_bullet = HeroBullets(screen, hero, hero.direction, offset_x,
                                                  load_sprite_sheets("bullets", 32, 32, True))
                    new_hero_bullet.add(hero_bullets)

        hero_move(hero, objects, persons)
        bullets_update(hero_bullets, objects, persons)
        draw(screen, hero, persons, objects, hero_bullets, offset_x)
        clock.tick(FPS)

        if (hero.rect.right - offset_x >= WIDTH - scroll_area_width and hero.x_vel > 0) or (
                hero.rect.left - offset_x <= scroll_area_width and hero.x_vel < 0):
            offset_x += hero.x_vel

        for i in range(len(persons)):
            if persons[i].dead:
                persons.pop(i)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
