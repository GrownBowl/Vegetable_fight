import sqlite3
from objects import WoodBlock, ThornsBlock, UpDownBlock, DropBlock, FinishBlock
from personages import Hero, Tomato, Broccoli, Pumpkin, Eggplant


def create_first_level(block_size, screen_width, screen_height, woods, thorns, up_down, drop, hero, tomato, pumpkin,
                       eggplant, broccoli=None):
    """Функция возвращающая все объекты первого уровня"""
    # Подключение к БД
    con = sqlite3.connect("database/date.sqlite3")
    # Создание курсора
    cur = con.cursor()
    # Выполнение запроса и получение всех результатов
    result = cur.execute("""SELECT id, collected FROM drops
    WHERE level = 1""").fetchall()
    con.close()

    drop_obj = []
    if not result[0][1]:
        drop_obj += [DropBlock(7 * block_size, screen_height - 7 * block_size, block_size, drop, 1)]

    if not result[1][1]:
        drop_obj += [DropBlock(16.4 * block_size, screen_height - 10 * block_size, block_size, drop, 2)]

    if not result[2][1]:
        drop_obj += [DropBlock(42 * block_size, screen_height - 7 * block_size, block_size, drop, 3)]

    first = [WoodBlock(i * block_size, screen_height - 6 * block_size, block_size, woods) for i in range(12)]
    second = [WoodBlock(i * block_size, screen_height - 11 * block_size, block_size, woods) for i in range(8, 10)]
    third = [WoodBlock(i * block_size, screen_height - 9 * block_size, block_size, woods) for i in range(13, 18)]
    fourth = [WoodBlock(i * block_size, screen_height - 8 * block_size, block_size, woods) for i in range(18, 21)]
    fifth = [WoodBlock(i * block_size, screen_height - 5 * block_size, block_size, woods) for i in range(25, 28)]
    sixth = [WoodBlock(i * block_size, screen_height - 7 * block_size, block_size, woods) for i in range(29, 35)]
    seventh = [WoodBlock(i * block_size, screen_height - 8 * block_size, block_size, woods) for i in range(36, 38)]
    eight = [WoodBlock(i * block_size, screen_height - 10 * block_size, block_size, woods) for i in range(39, 41)]
    ninth = [WoodBlock(i * block_size, screen_height - 12 * block_size, block_size, woods) for i in range(42, 44)]
    tenth = [WoodBlock(i * block_size, screen_height - 6 * block_size, block_size, woods) for i in range(41, 43)]
    eleventh = [WoodBlock(i * block_size, screen_height - 1 * block_size, block_size, woods) for i in range(46, 50)]
    twelfth = [WoodBlock(i * block_size, screen_height - 1 * block_size, block_size, woods) for i in range(52, 54)]
    thirteen = [WoodBlock(i * block_size, screen_height - 8 * block_size, block_size, woods) for i in range(55, 58)]
    thorns_obj = [ThornsBlock(i * block_size, screen_height - 1 * block_size, block_size, thorns) for i in
                  range(50, 52)] + [ThornsBlock(39 * block_size, 8 * block_size, block_size, thorns),
                                    ThornsBlock(40 * block_size, 7 * block_size, block_size, thorns),
                                    ThornsBlock(41 * block_size, 6 * block_size, block_size, thorns),
                                    ThornsBlock(42 * block_size, 5 * block_size, block_size, thorns),
                                    ThornsBlock(43 * block_size, 9 * block_size, block_size, thorns)]
    up_down_obj = [UpDownBlock(54 * block_size, screen_height - 1 * block_size, block_size, up_down, 7 * block_size)]
    finish = [FinishBlock(57 * block_size, screen_height - 9 * block_size, block_size, woods)]
    total_objects = [*first, *second, *third, *fourth, *fifth, *sixth, *seventh, *eight, *ninth, *tenth,
                     *eleventh, *twelfth, *thirteen, *thorns_obj, *up_down_obj, *drop_obj, *finish]
    persons = [Hero(0, 7 * block_size, 32, 32, hero),
               Tomato(15 * block_size, screen_height - 10.3 * block_size, 32, 32, "left", tomato),
               Pumpkin(31.5 * block_size, screen_height - 8.3 * block_size, 32, 32, "right", pumpkin, 2 * block_size),
               Eggplant(22.5 * block_size, screen_height - 7 * block_size, 32, 32, "up", eggplant, 3 * block_size),
               Broccoli(40 * block_size, screen_height - 11.3 * block_size, 32, 32, "left", broccoli)]

    return persons, total_objects


def create_second_level(block_size, screen_width, screen_height, woods, up_down, hero, tomato, pumpkin):
    first = [WoodBlock(i * block_size, screen_height - 6 * block_size, block_size, woods) for i in range(12)]
    second = [UpDownBlock(12 * block_size, screen_height - 6 * block_size, block_size, up_down, 7 * block_size)]
    pers = [Hero(0, 7 * block_size, 32, 32, hero)]

    total_odj = [*first, *second]

    return pers, total_odj