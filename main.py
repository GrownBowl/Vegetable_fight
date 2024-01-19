import os
import sys
import pygame
from personages import Hero
from random import randrange
from objects import ThornsBlock, SlowdownBlock, BoostBlock, UpDownBlock, LeftRightBlock, DropBlock
from byllets import Bullets
from levels import create_first_level

# Инициализация pygame и констант
pygame.init()
FPS = 60
SIZE = WIDTH, HEIGHT = 1280, 720
HERO_SPEED = 5
TIME_COUNT = 0
DROP_COUNT = 0

screen = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
hero_bullets = pygame.sprite.Group()
tomato_bullets = pygame.sprite.Group()


def terminate():
    """Функция закрытия окна"""

    pygame.quit()
    sys.exit()


def draw_background(bck):
    """Функция отрисовки заднего фона"""

    screen.blit(bck, (0, 0))


def flip_image(sprites):
    """Функция отзеркаливания изображения"""

    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_block(size, name_block):
    """Функция загрузки блоков"""

    path = os.path.join("assets", "objects", name_block)
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, size, size)
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


def draw(screen, hero, persons, objects, her_bullets, tomat_bullet, offset_x, hp, drop):
    """Функция отрисовки всего на экране"""

    # Отрисовываем объекты
    for obj in objects:
        obj.draw(screen, offset_x)
        if type(obj) == UpDownBlock or type(obj) == LeftRightBlock:
            obj.update()

    # Отрисовываем пули
    for bullet in her_bullets.sprites():
        bullet.draw(screen, offset_x)

    for tom_bullet in tomat_bullet.sprites():
        tom_bullet.draw(screen, offset_x)

    # Отрисовываем персонажей
    for person in persons:
        person.draw(screen, offset_x)

    # Отрисовываем главного героя
    hero.draw(screen, offset_x)

    # Отрисовываем хп главноого героя исходя из их количества
    for i in range(hero.get_hp()):
        screen.blit(hp, (i * 55 + 10, 10))

    # Отричовываем капельки исходя из их собранного количсетва
    for i in range(1, DROP_COUNT + 1):
        screen.blit(drop, (WIDTH - 40 * i - 10, 10))

    pygame.display.flip()


def vertical_collision(hero, objects, dy):
    """Функция проверки на вертикальное столковения. Возвращает все объекты, с которыми произошло столкновение"""

    collided_objects = []
    for obj in objects:
        # Если объект не капелька, то проверяем столкновение
        if type(obj) != DropBlock:
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
    """Функция возвращающая объект, с которым произошло столкновение"""
    hero.move(dx, 0)
    hero.update()
    collided_object = None

    if type(objects) != Hero:
        for obj in objects:
            if pygame.sprite.collide_mask(hero, obj):
                collided_object = obj
                break

    else:
        if pygame.sprite.collide_mask(hero, objects):
            collided_object = objects

    hero.move(-dx, 0)
    hero.update()
    return collided_object


def bullets_update(hero_bullets, tomat_bullets, objects, persons, hero):
    """Обновление позиций пуль"""

    for bullet in hero_bullets.copy():
        collide_person = collide(bullet, persons, bullet.speed)
        # Если пуля столкнулась с персонажем, то она удаляется
        if collide_person:
            hero_bullets.remove(bullet)
            collide_person.hit()

        # Если пуля столкнулась с объектом на карте, то она удаляется
        if collide(bullet, objects, bullet.speed):
            hero_bullets.remove(bullet)

        # Если пуля вышла за границы карты, то она удаляется
        if bullet.get_position_x() > 3000 or bullet.get_position_x() < 0:
            hero_bullets.remove(bullet)

    for bullet in tomat_bullets.copy():
        # Если пуля томата столкулась с главным героем,
        # то главному герою наносится урон и пуля удяляется из общего списка
        if collide(bullet, hero, bullet.speed):
            hero.make_hit()
            tomato_bullets.remove(bullet)

        # Если пуля столкнулась с объектом на карте, то она удаляется
        if collide(bullet, objects, bullet.speed):
            tomato_bullets.remove(bullet)

        # Если пуля вышла за границы карты, то она удаляется
        if bullet.get_position_x() > 3000 or bullet.get_position_x() < 0:
            tomato_bullets.remove(bullet)

    hero_bullets.update()


def hero_move(hero, objects, persons):
    """Обновление героя, проверка на столкновения"""

    global TIME_COUNT, HERO_SPEED, DROP_COUNT

    # Обновление анимаций
    for person in persons:
        person.update_sprite()

    hero.loop(FPS)
    keys = pygame.key.get_pressed()

    hero.x_vel = 0
    # Получаем объекты, с которым столкнулся персонаж
    collide_left = collide(hero, objects, -HERO_SPEED * 2)
    collide_right = collide(hero, objects, HERO_SPEED * 2)

    # Если персонаж столкнулся с капелькой, то обновляем счетчик собранных капель. Обнуляем объекты
    if type(collide_left) == DropBlock:
        DROP_COUNT += 1
        ind_drop = objects.index(collide_left)
        objects.pop(ind_drop)
        collide_left = None
    if type(collide_right) == DropBlock:
        DROP_COUNT += 1
        ind_drop = objects.index(collide_right)
        objects.pop(ind_drop)
        collide_right = None

    # Передвигаем персонажа, если он не пересекается с другими объектами
    if keys[pygame.K_a] and not collide_left:
        hero.move_left(HERO_SPEED)
    if keys[pygame.K_d] and not collide_right:
        hero.move_right(HERO_SPEED)

    vertical_collision(hero, objects, hero.y_vel)

    to_check = [collide_left, collide_right]

    for obj in to_check:
        # Если персонаж столкнулся с шипами, то он умирает
        if obj and type(obj) == ThornsBlock:
            hero.die()
        # Или же с блоком замедления, то его скорость уменьшается. Счетчик времени обнуляется
        elif obj and type(obj) == SlowdownBlock:
            TIME_COUNT = 0
            HERO_SPEED = 2
        # Или же с блоком ускорения, то его скорость увеличивается. Счетчик времени обнуляется
        elif obj and type(obj) == BoostBlock:
            TIME_COUNT = 0
            HERO_SPEED = 8


def start_screen(fon):
    """Функция, запускающая стартовый экран"""

    intro_text = ["Прототип главного экрана игры", "",
                  "Для начала игры нажмите любую клавишу"]
    draw_background(fon)
    font = pygame.font.Font(None, 30)
    text_coord = 50
    # Отрисовывем текст
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # Начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def main():
    """Главная функция"""

    global TIME_COUNT, HERO_SPEED, DROP_COUNT
    DROP_COUNT = 0

    # Загружаем задний фон, хп, капельку
    bck = pygame.image.load("assets/Bez_imeni-2.png")
    hp = pygame.image.load("assets/objects/heart.png")
    drop = pygame.image.load("assets/objects/drop.png")
    drop = pygame.transform.scale(drop, (50, 50))

    running = True

    block_size = 48
    # Создаём уровень
    persons, objects = create_first_level(block_size, WIDTH, HEIGHT,
                                          woods=load_block(block_size, "wood.png"),
                                          thorns=load_block(block_size, "thorns.png"),
                                          up_down=load_block(block_size, "up_down.png"),
                                          drop=load_block(block_size, "drop.png"),
                                          hero=load_sprite_sheets("hero", 32, 32, True),
                                          tomato=load_sprite_sheets("tomato", 32, 32, True))
    hero = persons.pop(0)
    tomato = persons[0]

    offset_x = 0
    scroll_area_width = 200

    while running:
        if randrange(100) == 55 and not tomato.dead:
            new_tomato_bullet = Bullets(screen, tomato, tomato.direction, offset_x,
                                        load_sprite_sheets("bullets", 32, 32, True), "tomat_pellet_")
            new_tomato_bullet.add(tomato_bullets)

        # Отрисовываем задний фон
        draw_background(bck)

        for event in pygame.event.get():
            # Если нажата кнопка выхода, то цикл завершается
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                # Если нажат пробел, то персонаж прыгает
                if event.key == pygame.K_SPACE and hero.jump_count < 2:
                    hero.jump()

                # Если нажата кнопка s, то создаётся пуля
                if event.key == pygame.K_s:
                    new_hero_bullet = Bullets(screen, hero, hero.direction, offset_x,
                                              load_sprite_sheets("bullets", 32, 32, True), "potato_pellet_")
                    new_hero_bullet.add(hero_bullets)

        hero_move(hero, objects, persons)
        # Обновляем созданные пули
        bullets_update(hero_bullets, tomato_bullets, objects, persons, hero)
        # Отрисовываем все объекты
        draw(screen, hero, persons, objects, hero_bullets, tomato_bullets, offset_x, hp, drop)
        clock.tick(FPS)
        # Обновляем счётчик времени
        TIME_COUNT += 1
        # Если счётчик времени равен 250, то возвращаем нормальную скорость
        if TIME_COUNT == 250:
            HERO_SPEED = 5

        if (hero.rect.right - offset_x >= WIDTH - scroll_area_width and hero.x_vel > 0) or (
                hero.rect.left - offset_x <= scroll_area_width and hero.x_vel < 0):
            offset_x += hero.x_vel

        # Если персонаж умер, то удаляем его из списка всех персонажей
        for i in range(len(persons)):
            if persons[i].dead:
                persons.pop(i)

        # Если у персонажа закончились хп, то запускаем главный экран
        if hero.get_hp() == 0:
            clock.tick(1)
            start_screen(bck)
            main()

    terminate()


if __name__ == '__main__':
    main()
