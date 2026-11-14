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

# Переходы направлений: (текущее, клавиша) -> новое.
# Пары с разворотом на 180° отсутствуют намеренно.
DIRECTION_KEYS = {
    (LEFT, pg.K_UP): UP,
    (RIGHT, pg.K_UP): UP,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_DOWN): DOWN,
    (UP, pg.K_LEFT): LEFT,
    (DOWN, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_RIGHT): RIGHT,
}

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20
# Границы и шаг изменения скорости:
MIN_SPEED = 5
MAX_SPEED = 60
SPEED_STEP = 5

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption(
    'Змейка. +/- для изменения скорости игры. ESC для выхода'
)

# Настройка времени:
clock = pg.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Базовый класс для всех игровых объектов.
    Хранит позицию объекта на игровом поле и его цвет.
    По умолчанию объект располагается в центре экрана.
    """

    def __init__(self, body_color=None):
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color

    def draw_cell(self, position, color, border_color=BORDER_COLOR):
        """Рисует одну клетку сетки с опциональным контуром.

        Args:
            position: координаты (x, y) левого верхнего угла клетки.
            color: цвет заливки клетки.
            border_color: цвет контура. Если None или совпадает
                с color, контур не рисуется — это позволяет
                использовать метод и для стирания клетки.
        """
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        if border_color is not None and border_color != color:
            pg.draw.rect(screen, border_color, rect, 1)

    def draw(self):
        """Отрисовывает объект на экране.
        Базовый класс ничего не рисует — метод переопределяется
        в дочерних классах.
        """
        raise NotImplementedError(
            f'{type(self).__name__}.draw() не реализован в дочернем классе'
        )


class Apple(GameObject):
    """Игровое яблоко, которое собирает змейка.
    Яблоко занимает одну клетку сетки и при съедании
    перемещается в случайную свободную позицию.
    """

    def __init__(self, occupied_cells=None):
        super().__init__(APPLE_COLOR)
        self.randomize_position(occupied_cells or [])

    def randomize_position(self, occupied_cells):
        """
        Случайным образом выбираем позицию яблока, делим поле по клетках
        и выбираем случайным образом
        """
        while True:
            self.position = (
                randint(0, SCREEN_WIDTH // GRID_SIZE - 1) * GRID_SIZE,
                randint(0, SCREEN_HEIGHT // GRID_SIZE - 1) * GRID_SIZE,
            )
            if self.position not in occupied_cells:
                break

    def draw(self):
        """Рисуем яблоко."""
        self.draw_cell(self.position, self.body_color)


class Snake(GameObject):
    """
    Змейка — управляемый игроком персонаж.
    Состоит из списка сегментов, где первый элемент - голова.
    """

    def __init__(self):
        super().__init__()
        self.body_color = SNAKE_COLOR
        self.speed = SPEED
        self.reset()
        self.direction = RIGHT

    def reset(self):
        """Возвращает змейку в начальное состояние.
        Длина сбрасывается до 1, тело состоит из одной клетки
        в центре экрана, направление выбирается случайным образом
        из четырёх возможных.
        """
        self.length = 1
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None

    def get_head_position(self) -> tuple[int, int]:
        """Возращаем позицию головы."""
        return self.positions[0]

    def move(self) -> None:
        """
        Получаем текущую позицию, головы и вычисляем координаты новой
        в зависимости от направления.
        """
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction
        self.positions.insert(
            0,
            (
                (head_x + direction_x * GRID_SIZE) % SCREEN_WIDTH,
                (head_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT,
            ),
        )
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    # Метод draw класса Snake
    def draw(self):
        """Отрисовывает змейку: затирает ушедший хвост и рисует голову."""
        if self.last:
            self.draw_cell(
                self.last, BOARD_BACKGROUND_COLOR, border_color=None
            )
        self.draw_cell(self.get_head_position(), self.body_color)


def handle_keys(game_object):
    """Обрабатывает события клавиатуры и возвращает новое направление.

    Стрелки задают направление движения по таблице DIRECTION_KEYS;
    Клавиши «+» и «-» меняют скорость змейки в пределах
    MIN_SPEED..MAX_SPEED. Клавиша ESC и закрытие окна завершают игру.

    Returns:
        Актуальное направление движения после обработки ввода.
    """
    direction = game_object.direction
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                raise SystemExit
            elif event.key in (pg.K_PLUS, pg.K_EQUALS, pg.K_KP_PLUS):
                game_object.speed = min(
                    game_object.speed + SPEED_STEP, MAX_SPEED
                )
            elif event.key in (pg.K_MINUS, pg.K_KP_MINUS):
                game_object.speed = max(
                    game_object.speed - SPEED_STEP, MIN_SPEED
                )
            else:
                direction = DIRECTION_KEYS.get(
                    (direction, event.key), direction
                )
    return direction


def main():
    """
    Запускает основной игровой цикл
    Обрабатываются события клавиатуры.
    Обновляется направление движения змейки.
    Змейка перемещается.
    Проверяется, съела ли змейка яблоко.
    Проверяются столкновения змейки с собой.
    Отрисовываются объекты.
    Экран обновляется.
    """
    snake = Snake()
    apple = Apple(snake.positions)

    while True:
        clock.tick(snake.speed)
        # Обработка ввода и обновление направления
        snake.update_direction(handle_keys(snake))
        # Перемещение змейки
        snake.move()

        # Съедание яблока
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
        # Столкновение с собой
        elif snake.get_head_position() in snake.positions[3:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)
        # Отрисовка объектов
        apple.draw()
        snake.draw()
        # Обновление экрана
        pg.display.update()


if __name__ == '__main__':
    main()
