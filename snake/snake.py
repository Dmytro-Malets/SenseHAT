from sense_hat import SenseHat
from time import sleep
import random

sense = SenseHat()
sense.clear()

RED = (190, 0, 0)
GREEN = (0, 190, 0)
BLACK = (0, 0, 0)
WHITE = (190, 190, 190)
BLUE = (0, 0, 190)

LEVEL_CONFIG = {
    1: {
        'target_length': 15,
        'initial_sleep_time': 1.0,
        'start_pos': (2, 4),
        'direction': "right",
        'walls_config': None
    },
    2: {
        'target_length': 15,
        'initial_sleep_time': 0.9,
        'start_pos': (3, 4),
        'direction': "up",
        'walls_config': lambda: [(2, y + 2) for y in range(4)] + [(5, y + 2) for y in range(4)]
    },
    3: {
        'target_length': 15,
        'initial_sleep_time': 0.8,
        'start_pos': (3, 4),
        'direction': "left",
        'walls_config': lambda: (
                [(x + 2, 2) for x in range(4)] +
                [(x + 2, 5) for x in range(4)] +
                [(0, 0), (0, 1), (1, 0), (6, 0), (7, 0), (7, 1),
                 (0, 6), (0, 7), (1, 7), (6, 7), (7, 6), (7, 7)]
        )
    },
    4: {
        'target_length': 15,
        'initial_sleep_time': 0.7,
        'start_pos': (1, 1),
        'direction': "right",
        'walls_config': lambda: (
                [(x, 0) for x in range(8)] +
                [(x, 7) for x in range(8)] +
                [(0, y + 1) for y in range(6)] +
                [(7, y + 1) for y in range(6)] +
                [(3, 3), (4, 4), (3, 4), (4, 3)]
        )
    },
    5: {
        'target_length': 15,
        'initial_sleep_time': 0.6,
        'start_pos': (5, 4),
        'direction': "right",
        'walls_config': lambda: (
                [(x + 1, 1) for x in range(6)] +
                [(x + 1, 6) for x in range(6)] +
                [(3, 3), (4, 4), (3, 4), (4, 3), (1, 2), (6, 2),
                 (1, 5), (6, 5), (3, 0), (4, 0), (3, 7), (4, 7)]
        )
    },
}


class SnakeGame:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.level = 1
        self.reset_level(self.level)

    def reset_level(self, level):
        config = LEVEL_CONFIG[level]
        self.snake = [config['start_pos']]
        self.snake_length = 1
        self.direction = config['direction']
        self.food = None
        self.walls = []
        self.sleep_time = config['initial_sleep_time']
        if config['walls_config']:
            self.walls = config['walls_config']()

    def generate_food(self):
        while True:
            x = random.randint(0, 7)
            y = random.randint(0, 7)
            if (x, y) not in self.snake and (x, y) not in self.walls:
                self.food = (x, y)
                return

    def move(self):
        x, y = self.snake[0]

        moves = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0)
        }

        dx, dy = moves[self.direction]
        x = (x + dx) % 8
        y = (y + dy) % 8

        if (x, y) in self.snake or (x, y) in self.walls:
            return False

        self.snake.insert(0, (x, y))

        if (x, y) == self.food:
            self.snake_length += 1
            if self.sleep_time > 0.3:
                self.sleep_time *= 0.97
            self.generate_food()

        if len(self.snake) > self.snake_length:
            self.snake.pop()

        return True

    def draw(self):
        sense.clear()
        for wall in self.walls:
            sense.set_pixel(wall[0], wall[1], BLUE)
        for i, segment in enumerate(self.snake):
            color = WHITE if i == 0 else GREEN
            sense.set_pixel(segment[0], segment[1], color)
        if self.food:
            sense.set_pixel(self.food[0], self.food[1], RED)

    def handle_events(self):
        opposite_directions = {
            "up": "down",
            "down": "up",
            "left": "right",
            "right": "left"
        }

        for event in sense.stick.get_events():
            if event.action == "pressed" and event.direction in opposite_directions:
                if opposite_directions[event.direction] != self.direction:
                    self.direction = event.direction

    def play_level(self, level):
        sense.stick.get_events()
        self.generate_food()

        while self.snake_length < LEVEL_CONFIG[level]['target_length']:
            self.handle_events()
            if self.move():
                self.draw()
            else:
                sense.show_message("Game Over!", text_colour=RED)
                return False
            sleep(self.sleep_time)

        self.level += 1
        return True

    def run(self):
        while True:
            if self.level <= 5:
                sense.show_message(str(self.level), text_colour=GREEN)
                self.reset_level(self.level)
                if not self.play_level(self.level):
                    break
            else:
                sense.show_message("You Win!", text_colour=GREEN)
                break
        sense.clear()


if __name__ == "__main__":
    game = SnakeGame()
    game.run()
