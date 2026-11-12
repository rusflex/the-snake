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
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption("Змейка")

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Базовый класс для всех игровых объектов.
    Хранит позицию объекта на игровом поле и его цвет.
    По умолчанию объект располагается в центре экрана.
    """

    position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def __init__(self, position=None, body_color=None):
        if position is None:
            position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Отрисовывает объект на экране.
        Базовый класс ничего не рисует — метод переопределяется
        в дочерних классах.
        """
        pass


class Apple(GameObject):
    """Игровое яблоко, которое собирает змейка.
    Яблоко занимает одну клетку сетки и при съедании
    перемещается в случайную свободную позицию.
    """

    def randomize_position(self):
        """
        Случайным образом выбираем позицию яблока, делим поле по клетках
        и выбираем случайным образом
        Returns:
            Кортеж (x, y) с координатами левого верхнего угла яблока.
        """
        cols = SCREEN_WIDTH // GRID_SIZE
        rows = SCREEN_HEIGHT // GRID_SIZE
        position = (
            randint(0, cols - 1) * GRID_SIZE,
            randint(0, rows - 1) * GRID_SIZE,
        )
        return position

    def __init__(self):
        super().__init__(self.randomize_position(), APPLE_COLOR)

    def draw(self):
        """Рисуем яблоко по размеру ячейки"""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Змейка — управляемый игроком персонаж.
    Состоит из списка сегментов (positions), где первый элемент -
    голова. Двигается в текущем направлении (direction), пока
    игрок не задаст новое направление через next_direction.
    """

    def __init__(self):
        super().__init__()
        self.body_color = SNAKE_COLOR
        self.reset()

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
        """Возращаем позицию головы"""
        return self.positions[0]

    def move(self) -> None:
        """
        Получаем текущую позицию, головы и вычисляем координаты новой
        в зависимости от направления
        """
        current_head_pos = self.get_head_position()
        head_x, head_y = current_head_pos
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def update_direction(self):
        """Метод обновления направления после нажатия на кнопку"""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    # Метод draw класса Snake
    def draw(self):
        """Отрисовывает змейку: тело, голову и затирает хвост."""
        for position in self.positions[:-1]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)


def handle_keys(game_object):
    """
    Обрабатывает события клавиатуры и закрытия окна.
    При нажатии стрелок задаёт новое направление движения
    в next_direction, если оно не противоположно текущему.
    При закрытии окна завершает работу программы.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif (event.key == pygame.K_DOWN
                  and game_object.direction != UP):
                game_object.next_direction = DOWN
            elif (
                event.key == pygame.K_LEFT
                and game_object.direction != RIGHT
            ):
                game_object.next_direction = LEFT
            elif (
                event.key == pygame.K_RIGHT
                and game_object.direction != LEFT
            ):
                game_object.next_direction = RIGHT


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
    apple = Apple()

    while True:
        clock.tick(SPEED)
        # Обработка ввода и обновление направления
        handle_keys(snake)
        snake.update_direction()
        # Перемещение змейки
        snake.move()

        # Съедание яблока
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.position = apple.randomize_position()
            # Если яблоко появляется в змейке, меняем позицию
            while apple.position in snake.positions:
                apple.position = apple.randomize_position()

        # Столкновение с собой
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
        # Отрисовка объектов
        apple.draw()
        snake.draw()
        # Обновление экрана
        pygame.display.update()


if __name__ == "__main__":
    main()
