from random import choice, randint

import pygame

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

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """
    Базовый класс для игровых объектов. Хранит общие атрибуты - позицию и цвет,
    а также заготовку метода отрисовки, которую переопределяют дочерние классы.
    """

    def __init__(self, body_color: tuple[int, int, int] = (0, 0, 0)):
        """
        Инициализирует базовые атрибуты объекта:
        позицию в центре экрана и цвет.
        """
        self.position: tuple[int, int] = (
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
        )
        self.body_color = body_color

    def draw(self):
        """Заготовка метода отрисовки. Переопределяется в дочерних классах."""
        pass


class Apple(GameObject):
    """
    Класс яблока — игрового объекта, который змейка должна съедать.
    Хранит координаты яблока на игровом поле
    и умеет случайным образом менять свою позицию после того, как его съели.
    """

    def __init__(self):
        """
        Инициализирует яблоко цветом
        и случайной позицией на игровом поле.
        """
        super().__init__(APPLE_COLOR)
        self.randomize_position()

    def randomize_position(self):
        """
        Устанавливает случайную позицию яблока в пределах игрового поля,
        кратную размеру клетки.
        """
        x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
        y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        self.position = (x, y)

    def draw(self):
        """Отрисовывает яблоко на игровом поле в виде квадрата с обводкой."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """
    Класс змейки — основной игровой объект.
    Хранит список сегментов тела, текущее и следующее направление движения,
    отвечает за перемещение по полю, рост после съеденного яблока,
    проверку столкновений и сброс игры в начальное состояние.
    """

    def __init__(self):
        """
        Инициализирует змейку: цвет, длину, список сегментов,
        направление движения и вспомогательные атрибуты.
        """
        super().__init__(SNAKE_COLOR)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """
        Возвращает координаты головы змейки
        - первый элемент списка сегментов.
        """
        return self.positions[0]

    def move(self):
        """
        Вычисляет новую позицию головы змейки в текущем направлении,
        добавляет её в начало списка сегментов и удаляет последний сегмент,
        если длина змейки не увеличилась.
        """
        head_position = self.get_head_position()
        head_x, head_y = head_position
        dx, dy = self.direction
        new_x = (head_x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (new_x, new_y)
        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def update_direction(self):
        """
        Обновляет направление движения змейки на основе направления,
        выбранного пользователем.
        """
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def draw(self):
        """
        Отрисовывает все сегменты змейки на игровом поле
        и затирает клетку последнего удалённого сегмента.
        """
        for position in self.positions[1:]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def reset(self):
        """
        Сбрасывает змейку в начальное состояние:
        длина 1, позиция в центре экрана, случайное направление движения.
        """
        self.length = 1
        self.positions = [self.position]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None


def handle_keys(game_object):
    """
    Обрабатывает нажатия клавиш пользователем
    и обновляет следующее направление движения игрового объекта.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """
    Инициализирует игру и запускает основной игровой цикл,
    в котором обрабатываются события,
    обновляется состояние объектов и отрисовывается игровое поле.
    """
    pygame.init()

    apple = Apple()
    snake = Snake()

    while True:
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            continue

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position()
        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()

        pygame.display.update()
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
