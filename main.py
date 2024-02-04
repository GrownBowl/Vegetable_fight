import os
import sqlite3
import sys
import pygame
import pygame_gui
from personages import Hero, Pumpkin, Eggplant, Onion
from random import randrange
from objects import ThornsBlock, SlowdownBlock, BoostBlock, UpDownBlock, LeftRightBlock, DropBlock, FinishBlock, Hp
from byllets import Bullets, BroccoliBullet
from levels import create_first_level, create_second_level


def get_count_collected_drop() -> int:
    count = 0
    # Подключение к БД
    con = sqlite3.connect("database/date.sqlite3")
    # Создание курсора
    cur = con.cursor()
    # Выполнение запроса и получение всех результатов
    result = cur.execute("""SELECT collected FROM drops""").fetchall()
    con.close()

    for elem in result:
        if elem[0]:
            count += 1
    return count


# Инициализация pygame и констант
pygame.mixer.pre_init()
pygame.init()
pygame.display.set_caption("VegetableFight")
FPS = 60
SIZE = WIDTH, HEIGHT = 1280, 720
HERO_SPEED = 5
TIME_COUNT = 0
DROP_COUNT = get_count_collected_drop()
LEVEL = 0
drops_id = []

screen = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
hero_bullets = pygame.sprite.Group()
tomato_bullets = pygame.sprite.Group()
broccoli_bullets = pygame.sprite.Group()

# Инициализация звуковых эффектов
dead_sound = pygame.mixer.Sound("sounds/dead.ogg")
dead_sound.set_volume(0.1)
hit_sound = pygame.mixer.Sound("sounds/hit.ogg")
hit_sound.set_volume(0.1)
kill_sound = pygame.mixer.Sound("sounds/kill.ogg")
kill_sound.set_volume(0.4)
picked_sound = pygame.mixer.Sound("sounds/picked.ogg")
picked_sound.set_volume(0.3)
shoot_sound = pygame.mixer.Sound("sounds/shoot.ogg")
shoot_sound.set_volume(0.1)
win_sound = pygame.mixer.Sound("sounds/win.ogg")
win_sound.set_volume(0.1)


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


def draw(screen, hero, persons, objects, her_bullets, tomat_bullet, broc_bullet, offset_x, hp, drop):
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

    for br_bullet in broc_bullet.sprites():
        br_bullet.draw(screen, offset_x)

    # Отрисовываем персонажей, если он жив
    for person in persons:
        if not person.dead:
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
        if type(obj) != DropBlock and type(obj) != Hp:
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

    if type(objects) != Hero and type(objects) != Pumpkin and type(objects) != Eggplant:
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


def bullets_update(hero_bullets, tomat_bullets, broc_bullets, objects, persons, hero):
    """Обновление позиций пуль"""

    for bullet in hero_bullets.copy():
        collide_person = collide(bullet, persons, bullet.speed)
        # Если пуля столкнулась с персонажем, то она удаляется
        if collide_person:
            hero_bullets.remove(bullet)
            kill_sound.play()
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
            hit_sound.play()
            hero.make_hit()
            tomato_bullets.remove(bullet)

        # Если пуля столкнулась с объектом на карте, то она удаляется
        if collide(bullet, objects, bullet.speed):
            tomato_bullets.remove(bullet)

        # Если пуля вышла за границы карты, то она удаляется
        if bullet.get_position_x() > 3000 or bullet.get_position_x() < 0:
            tomato_bullets.remove(bullet)

    for bullet in broc_bullets.copy():
        # Если пуля брокколи столкулась с главным героем,
        # то главному герою наносится урон и пуля удяляется из общего списка
        if collide(bullet, hero, bullet.speed):
            hit_sound.play()
            hero.make_hit()
            broccoli_bullets.remove(bullet)

        # Если пуля столкнулась с объектом на карте, то она удаляется
        if collide(bullet, objects, bullet.speed):
            broccoli_bullets.remove(bullet)

        # Если пуля вышла за границы карты, то она удаляется
        if bullet.get_position_x() > 3000 or bullet.get_position_x() < 0:
            broccoli_bullets.remove(bullet)

    hero_bullets.update()


def mark_collected_drops():
    # Подключение к БД
    con = sqlite3.connect("database/date.sqlite3")
    # Создание курсора
    cur = con.cursor()
    for id_drop in drops_id:
        # Выполнение запроса, заполняем собранные капельки
        cur.execute("""
        UPDATE drops
        SET collected = 1
        WHERE id = ?""", (id_drop,)).fetchall()
    con.commit()
    con.close()


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
    collide_persons = collide(hero, persons, HERO_SPEED)

    # Если персонаж столкнулся с капелькой, то обновляем счетчик собранных капель. Обнуляем объекты
    if type(collide_left) == DropBlock:
        picked_sound.play()
        DROP_COUNT += 1
        ind_hp = objects.index(collide_left)
        objects.pop(ind_hp)
        drops_id.append(collide_left.get_id())
        collide_left = None
    if type(collide_right) == DropBlock:
        picked_sound.play()
        DROP_COUNT += 1
        ind_hp = objects.index(collide_right)
        objects.pop(ind_hp)
        drops_id.append(collide_right.get_id())
        collide_right = None

    # Если персонаж столкнулся с хп, то добавляем хп если их меньше 3-х. Обнуляем объекты
    if type(collide_left) == Hp:
        if hero.get_hp() < 3:
            picked_sound.play()
            hero.hp += 1
            ind_hp = objects.index(collide_left)
            objects.pop(ind_hp)
        collide_left = None
    if type(collide_right) == Hp:
        if hero.get_hp() < 3:
            picked_sound.play()
            hero.hp += 1
            ind_hp = objects.index(collide_right)
            objects.pop(ind_hp)
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
        # Или же с блоком финиша, то запускаем звук и меню победы
        elif obj and type(obj) == FinishBlock:
            mark_collected_drops()
            pygame.mixer.music.stop()
            win_sound.play()
            second_screen(False)

    # Если персонаж столкнулся с тыквой и до этого не сталкивался, то запускаем звук урона и наносим урон персонажу
    if type(collide_persons) == Pumpkin and not hero.collide_with_pumpkin:
        hit_sound.play()
        hero.make_hit()
        hero.collide_with_pumpkin = True
    # Если персонаж столкнулся не с тыквой, то collide_with_pumpkin ставим лож
    if type(collide_persons) != Pumpkin and hero.collide_with_pumpkin:
        hero.collide_with_pumpkin = False

    # Если персонаж столкнулся с баклажаном и до этого не сталкивался, то запускаем звук урона и наносим урон персонажу
    if type(collide_persons) == Eggplant and not hero.collide_with_eggplant:
        hit_sound.play()
        hero.make_hit()
        hero.collide_with_eggplant = True
    # Если персонаж столкнулся не с баклажаном, то collide_with_pumpkin ставим лож
    if type(collide_persons) != Eggplant and hero.collide_with_eggplant:
        hero.collide_with_eggplant = False

    # Если перосонаж столкнулся с луком, то уменьшаем скорость, счётчик времени ставим 0
    if type(collide_persons) == Onion:
        TIME_COUNT = 0
        HERO_SPEED = 2


def start_screen() -> int:
    """Функция, запускающая стартовый экран"""

    global LEVEL
    # Заргужаем фоновый звук, проигрываем его
    pygame.mixer.music.load("sounds/main_menu.ogg")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.1)

    # Загружаем фон, ставим цвет
    background = pygame.Surface(SIZE)
    background.fill(pygame.Color("#4C6FC9"))

    # Заргужаем шрифт, ставим текст
    name_font = pygame.font.Font("fonts/JotiOne-Regular.ttf", 48)
    name_text = name_font.render("Vegetable fight", 1, (255, 255, 255))

    # Инициализируем UIManager
    manager = pygame_gui.UIManager(SIZE, "theme.json")

    # Делаем текст
    text = pygame.font.Font(None, 36).render("Выберите уровень", 1, (255, 255, 255))

    # Создаём три кнопки
    first_level_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((160, 460), (250, 100)),
        text="1 level",
        manager=manager
    )

    second_level_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((515, 460), (250, 100)),
        text="2 level",
        manager=manager
    )

    third_level_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((870, 460), (250, 100)),
        text="3 level",
        manager=manager
    )

    # Основной цикл
    while True:
        time_delta = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            # Если нажата кнопка "1 level" запускаем первый лвл, останавливаем фоновую музыку
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == first_level_button:
                        LEVEL = 1
                        pygame.mixer.music.stop()
                        return 1
                    # Если нажата кнопка "2 level" запускаем второй лвл, останавливаем фоновую музыку
                    if event.ui_element == second_level_button:
                        LEVEL = 2
                        pygame.mixer.music.stop()
                        return 2

            manager.process_events(event)
        # Обновляем менеджер и отрисовываем текст
        manager.update(time_delta)
        screen.blit(background, (0, 0))
        screen.blit(name_text, (449, 231))
        screen.blit(text, (520, 336))
        manager.draw_ui(screen)
        pygame.display.update()


def second_screen(die_menu):
    """Функция отображающее меню проигрыша (die_menu = True), и меню выигрыша (die_menu = False)"""

    # Загружаем фон, ставим цвет
    background = pygame.Surface(SIZE)
    background.fill(pygame.Color("#D63535" if die_menu else "#41BA17"))

    # Загружаем шрифт, ставим текст
    name_text = pygame.font.Font("fonts/Roboto_bolt.ttf", 64).render("ВЫ ПРОИГРАЛИ!" if die_menu else "ВЫ ВЫИГРАЛИ!",
                                                                     1, (255, 255, 255))

    # Инициализируем UImanager
    manager = pygame_gui.UIManager(SIZE, "theme2.json")

    # Ставим дополнительный текст
    text1 = pygame.font.Font("fonts/Roboto.ttf", 32).render("Начать уровень заново", 1, (255, 255, 255))
    text2 = pygame.font.Font("fonts/Roboto.ttf", 32).render("Выйти в главное меню", 1, (255, 255, 255))

    # Создаём две кнопки
    again_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((340, 390), (150, 100)),
        text="1",
        manager=manager)

    main_menu_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((790, 390), (150, 100)),
        text="2",
        manager=manager
    )

    # Основной цикл
    while True:
        time_delta = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    # Если нажата кнопка "начать заново", то запускаем уровень заново
                    if event.ui_element == again_button:
                        main(LEVEL)
                    # Если нажата кнопка "выйти в главное меню", то запускаем главное меню

                    if event.ui_element == main_menu_button:
                        main(start_screen())

            manager.process_events(event)
        # Обновляем менеджер и отрисовываем текст
        manager.update(time_delta)
        screen.blit(background, (0, 0))
        screen.blit(name_text, (385, 110))
        screen.blit(text1, (227, 528))
        screen.blit(text2, (683, 528))
        manager.draw_ui(screen)
        pygame.display.update()


def run_level(bck, hp, drop, personages, objects, lvl):
    global HERO_SPEED, TIME_COUNT, DROP_COUNT

    # загружаем и проигрываем музыку
    pygame.mixer.music.load("sounds/game_back.ogg")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.04)

    HERO_SPEED = 5

    # Инициализируем необходимых персонажей
    tomato = None
    broccoli = None
    running = True

    hero = personages.pop(0)
    if lvl == 1:
        tomato = personages[0]
        broccoli = personages[3]

    offset_x = 0
    scroll_area_width = 200

    while running:
        # Обновляем счётчик времени
        TIME_COUNT += 1
        # Если уровень не второй и томат жив, и случайное число равно 55, то генерируем новую пулю
        if lvl != 2 and randrange(100) == 55 and not tomato.dead and lvl == 1:
            new_tomato_bullet = Bullets(screen, tomato, tomato.direction, offset_x,
                                        load_sprite_sheets("bullets", 32, 32, True), "tomat_pellet_")
            new_tomato_bullet.add(tomato_bullets)

        # Если уровень не второй и брокколи жив, и случайное число равно 38, то генерируем новую пулю
        if lvl != 2 and randrange(100) == 38 and not broccoli.dead:
            new_brocoli_bullet = BroccoliBullet(screen, broccoli, broccoli.direction, offset_x,
                                                load_sprite_sheets("bullets", 32, 32, True), "broccoli_pellet_")
            new_brocoli_bullet.add(broccoli_bullets)

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
                    shoot_sound.play()
                    new_hero_bullet = Bullets(screen, hero, hero.direction, offset_x,
                                              load_sprite_sheets("bullets", 32, 32, True), "potato_pellet_")
                    new_hero_bullet.add(hero_bullets)

        hero_move(hero, objects, personages)
        # Обновляем созданные пули
        bullets_update(hero_bullets, tomato_bullets, broccoli_bullets, objects, personages, hero)
        # Отрисовываем все объекты
        draw(screen, hero, personages, objects, hero_bullets, tomato_bullets, broccoli_bullets, offset_x, hp, drop)
        clock.tick(FPS)

        # Обновление камеры
        if (hero.rect.right - offset_x >= WIDTH - scroll_area_width and hero.x_vel > 0) or (
                hero.rect.left - offset_x <= scroll_area_width and hero.x_vel < 0):
            offset_x += hero.x_vel

        # Если счётчик времени равен 250, то ставим обычную скорость
        if TIME_COUNT == 250:
            HERO_SPEED = 5

        # Если персонаж умер, то удаляем его из списка
        for pers in personages:
            if pers.dead:
                personages.remove(pers)

        # Если персонаж находится ниже экрана, то он проигрывает
        if hero.get_position()[1] > WIDTH:
            pygame.mixer.music.stop()
            dead_sound.play()
            clock.tick(0.7)
            DROP_COUNT = get_count_collected_drop()
            second_screen(True)

        # Если у персонажа закончились хп, то запускаем главный экран
        if hero.get_hp() < 1:
            pygame.mixer.music.stop()
            dead_sound.play()
            clock.tick(1)
            DROP_COUNT = get_count_collected_drop()
            second_screen(True)

    terminate()


def main(level_num: int):
    """Главная функция"""

    # Загружаем задний фон, хп, капельку
    bck = pygame.image.load("assets/main_background.png")
    hp = pygame.image.load("assets/objects/heart.png")
    drop = pygame.image.load("assets/objects/drop.png")
    drop = pygame.transform.scale(drop, (50, 50))

    block_size = 48
    if level_num == 1:
        # Создаём уровень
        persons, objects = create_first_level(block_size, WIDTH, HEIGHT,
                                              woods=load_block(block_size, "wood.png"),
                                              thorns=load_block(block_size, "thorns.png"),
                                              up_down=load_block(block_size, "up_down.png"),
                                              drop=load_block(block_size, "drop.png"),
                                              hero=load_sprite_sheets("hero", 32, 32, True),
                                              tomato=load_sprite_sheets("tomato", 32, 32, True),
                                              pumpkin=load_sprite_sheets("pumpkin", 32, 32, True),
                                              eggplant=load_sprite_sheets("eggplant", 32, 32, False),
                                              broccoli=load_sprite_sheets("broccoli", 32, 32, True),
                                              onion=load_sprite_sheets("onion", 160, 64, True),
                                              hp=pygame.transform.scale(load_block(block_size, "heart.png"), (32, 32)))
        run_level(bck, hp, drop, persons, objects, 1)

    if level_num == 2:
        persons, objects = create_second_level(block_size, WIDTH, HEIGHT,
                                               load_block(block_size, "wood.png"),
                                               load_block(block_size, "up_down.png"),
                                               load_sprite_sheets("hero", 32, 32, True),
                                               load_sprite_sheets("tomato", 32, 32, True),
                                               load_sprite_sheets("pumpkin", 32, 32, True))
        run_level(bck, hp, drop, persons, objects, 2)


if __name__ == '__main__':
    main(start_screen())
