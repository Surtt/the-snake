"""Реализация игры «Змейка» на pygame."""

from random import choice, randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 10

# Клавиши и текущее направление → новое направление змейки
DIRECTION_KEYS = {
    (pg.K_UP, LEFT): UP,
    (pg.K_UP, RIGHT): UP,
    (pg.K_DOWN, LEFT): DOWN,
    (pg.K_DOWN, RIGHT): DOWN,
    (pg.K_LEFT, UP): LEFT,
    (pg.K_LEFT, DOWN): LEFT,
    (pg.K_RIGHT, UP): RIGHT,
    (pg.K_RIGHT, DOWN): RIGHT,
}

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов.

    Хранит общие атрибуты — позицию и цвет, а также заготовку метода
    отрисовки, которую переопределяют дочерние классы.
    """

    def __init__(
        self, body_color: tuple[int, int, int] = BOARD_BACKGROUND_COLOR
    ):
        """
        Инициализирует базовые атрибуты объекта:
        позицию в центре экрана и цвет.
        """
        self.position: tuple[int, int] = (
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
        )
        self.body_color = body_color

    def _draw_cell(self, position=None, color=None):
        """Отрисовывает одну клетку игрового поля.

        Если позиция или цвет не переданы, используются собственные
        значения объекта — self.position и self.body_color.
        """
        position = position or self.position
        color = color or self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Заготовка метода отрисовки. Переопределяется в дочерних классах."""
        raise NotImplementedError('Определите draw() в дочернем классе.')


class Apple(GameObject):
    """Класс яблока — игрового объекта, который змейка должна съедать.

    Хранит координаты яблока на игровом поле и умеет случайным
    образом менять свою позицию после того, как его съели.
    """

    def __init__(self, occupied_positions=None):
        """Инициализирует яблоко цветом и случайной позицией на поле."""
        super().__init__(APPLE_COLOR)
        if occupied_positions is None:
            occupied_positions = set()
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions):
        """Устанавливает случайную позицию яблока в пределах поля.

        Позиция кратна размеру клетки и не пересекается с занятыми
        клетками.
        """
        while True:
            position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )

            if position not in occupied_positions:
                break

        self.position = position

    def draw(self):
        """Отрисовывает яблоко на игровом поле в виде квадрата с обводкой."""
        self._draw_cell()


class Snake(GameObject):
    """Класс змейки — основной игровой объект.

    Хранит список сегментов тела, текущее и следующее направление
    движения, отвечает за перемещение по полю, рост после
    съеденного яблока, проверку столкновений и сброс игры
    в начальное состояние.
    """

    def __init__(self):
        """Инициализирует змейку: цвет, длину и список сегментов.

        Также задаёт направление движения и вспомогательные атрибуты.
        """
        super().__init__(SNAKE_COLOR)
        self.reset(RIGHT)

    def get_head_position(self):
        """Возвращает координаты головы — первый элемент списка."""
        return self.positions[0]

    def move(self):
        """Вычисляет новую позицию головы змейки.

        Добавляет её в начало списка сегментов и удаляет последний
        сегмент, если длина змейки не увеличилась.
        """
        head_position = self.get_head_position()
        head_x, head_y = head_position
        dx, dy = self.direction
        new_x = (head_x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (new_x, new_y)
        self.positions.insert(0, new_head)

        self.last = (
            self.positions.pop() if len(self.positions) > self.length else None
        )

    def update_direction(self, next_direction):
        """Обновляет направление движения змейки.

        Новое направление берётся из next_direction, выбранного
        пользователем.
        """
        if next_direction:
            self.direction = next_direction

    def draw(self):
        """Отрисовывает змейку на игровом поле.

        Также затирает клетку последнего удалённого сегмента.
        """
        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

        self._draw_cell(self.get_head_position())

    def reset(self, direction=None):
        """Сбрасывает змейку в начальное состояние.

        Устанавливает длину змейки равной 1, позицию — в центр экрана,
        случайное направление движения и очищает атрибут last.
        """
        self.length = 1
        self.positions = [self.position]
        self.direction = direction or choice((UP, DOWN, LEFT, RIGHT))
        self.last = None


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш пользователем.

    Возвращает выбранное пользователем направление движения,
    либо None, если направление не менялось.
    """
    next_direction = None
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit('Игра завершена пользователем')
        if event.type == pg.KEYDOWN:
            next_direction = DIRECTION_KEYS.get(
                (event.key, game_object.direction), next_direction
            )

    return next_direction


def main():
    """Инициализирует игру и запускает основной игровой цикл.

    В цикле обрабатываются события, обновляется положение змейки
    и яблока, проверяются столкновения и перерисовывается экран.
    """
    pg.init()

    snake = Snake()
    apple = Apple(snake.positions)
    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        next_direction = handle_keys(snake)
        snake.update_direction(next_direction)
        snake.move()

        head_position = snake.get_head_position()
        if head_position in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)
            continue

        if head_position == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
        apple.draw()
        snake.draw()

        pg.display.update()
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
