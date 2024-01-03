from objects import Block
from personages import Hero


def create_first_level(block_size, screen_width, screen_height, block, sprites):
    first = [Block(i * block_size, screen_height - 6 * block_size, block_size, block) for i in range(12)]
    second = [Block(i * block_size, screen_height - 11 * block_size, block_size, block) for i in range(8, 10)]
    third = [Block(i * block_size, screen_height - 9 * block_size, block_size, block) for i in range(13, 18)]
    fourth = [Block(i * block_size, screen_height - 8 * block_size, block_size, block) for i in range(18, 21)]
    fifth = [Block(i * block_size, screen_height - 5 * block_size, block_size, block) for i in range(25, 28)]
    sixth = [Block(i * block_size, screen_height - 7 * block_size, block_size, block) for i in range(29, 35)]
    seventh = [Block(i * block_size, screen_height - 8 * block_size, block_size, block) for i in range(36, 38)]
    eight = [Block(i * block_size, screen_height - 10 * block_size, block_size, block) for i in range(39, 41)]
    ninth = [Block(i * block_size, screen_height - 12 * block_size, block_size, block) for i in range(42, 44)]
    tenth = [Block(i * block_size, screen_height - 6 * block_size, block_size, block) for i in range(41, 43)]
    eleventh = [Block(i * block_size, screen_height - 1 * block_size, block_size, block) for i in range(46, 50)]
    twelfth = [Block(i * block_size, screen_height - 1 * block_size, block_size, block) for i in range(52, 54)]
    thirteen = [Block(i * block_size, screen_height - 8 * block_size, block_size, block) for i in range(56, 59)]
    total_objects = [*first, *second, *third, *fourth, *fifth, *sixth, *seventh, *eight, *ninth, *tenth,
                     *eleventh, *twelfth, *thirteen]

    return Hero(0, 7 * block_size, 32, 32, sprites), total_objects
