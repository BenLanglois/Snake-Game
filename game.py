import pygame, sys, random
from pygame.locals import *

# Constants/Settings -----------------------------------------------------------

HUMAN_PLAYER               = True
SHOW_BOARD = HUMAN_PLAYER or True
BOARD_SIZE                 = 32
BOX_SIZE                   = 15
FPS                        = 10
SEED                       = 1
WHITE                      = (255,255,255)
GREY                       = (127,127,127)
BLACK                      = (  0,  0,  0)
RED                        = (255,  0,  0)

# Class definitions ------------------------------------------------------------

class Box:
    def __init__(self, x, y):
        self.x, self.y = x, y

    @property
    def coords(self):
        return (self.x, self.y)

    @coords.setter
    def coords(self, pos):
        self.x, self.y = pos

    def __eq__(self, other):
        if type(other) == tuple and len(other) == 2:
            return self.coords == other
        elif type(other) == Box:
            return self.coords == other.coords
        else:
            return NotImplemented

    def __add__(self, other):
        if type(other) == tuple and len(other) == 2:
            return Box(self.x + other[0], self.y + other[1])
        else:
            return NotImplemented

    def draw(self, surface, colour):
        # Draw the box to screen
        rect = pygame.Rect(BOX_SIZE * self.x, BOX_SIZE * self.y, BOX_SIZE, BOX_SIZE)
        pygame.draw.rect(surface, colour, rect)

    def rand():
        return Box(random.randrange(BOARD_SIZE), random.randrange(BOARD_SIZE))

class Food(Box):
    def __init__(self, snake):
        self.move(snake)

    def draw(self, surface):
        # Draw the food to the screen
        Box.draw(self, surface, RED)

    def move(self, snake):
        # Move the food to a new position after being eaten
        new_box = Box.rand()
        while new_box == snake.head or new_box in snake.body:
            new_box = Box.rand()
        self.coords = new_box.coords

class Snake:
    def __init__(self):
        self.head = Box(BOARD_SIZE//2, BOARD_SIZE//2)
        self.body = []
        self.isAlive = True
        self.length = 1
        self.dir = (0, -1) # Up

    def _set_dir(self):
        if HUMAN_PLAYER:
            if last_press == K_UP:
                if self.dir != (0, 1): self.dir = (0, -1)
            elif last_press == K_DOWN:
                if self.dir != (0, -1): self.dir = (0, 1)
            elif last_press == K_LEFT:
                if self.dir != (1, 0): self.dir = (-1, 0)
            elif last_press == K_RIGHT:
                if self.dir != (-1, 0): self.dir = (1, 0)
        else:
            # Run neural net
            pass
        return (0, 0)

    def move(self, food):
        # Move the snake up, down, left, or right
        self._set_dir()
        new_head = self.head + self.dir

        if new_head in self.body[:-1] or -1 in new_head.coords or BOARD_SIZE in new_head.coords:
            # Collision
            self.isAlive = False

        elif new_head == food:
            # Grow snake
            self.length += 1
            self.body.append(self.head)
            self.head = new_head
            food.move(self)

        else:
            # Move snake
            self.body.append(self.head)
            self.head = new_head
            del self.body[0]

    def draw(self, surface):
        # Draw the snake to the display surface
        self.head.draw(surface, WHITE)
        for box in self.body:
            box.draw(surface, GREY)

# Helper functions -------------------------------------------------------------

# Reset game after game over
def reset_game():
    global snek, apple
    random.seed(SEED)
    snek = Snake()
    apple = Food(snek)

# Setup ------------------------------------------------------------------------

if SHOW_BOARD:
    pygame.init()
    screen = pygame.display.set_mode((BOARD_SIZE*BOX_SIZE, BOARD_SIZE*BOX_SIZE))
    pygame.display.set_caption("Snake game")
    clock = pygame.time.Clock()
    last_press = K_UP

reset_game()

# Main game loop ---------------------------------------------------------------

while True:
    if SHOW_BOARD:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key in (K_UP, K_DOWN, K_LEFT, K_RIGHT):
                last_press = event.key

    if snek.isAlive:
        snek.move(apple)

    if SHOW_BOARD:
        screen.fill(BLACK)
        snek.draw(screen)
        apple.draw(screen)

        pygame.display.update()
        clock.tick(FPS)