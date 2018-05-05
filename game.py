import pygame, sys, random
from pygame.locals import *

# Constants/Settings ----------------------

HUMAN_PLAYER               = True
SHOW_BOARD = HUMAN_PLAYER or True
BOARD_SIZE                 = 32
FPS                        = 5
SEED                       = 1
WHITE                      = (255,255,255)
GREY                       = (127,127,127)
BLACK                      = (  0,  0,  0)
RED                        = (255,  0,  0)

# Class definitions --------------

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

    def draw(self, screen, colour):
        # Draw the box to screen
        rect = pygame.Rect(10*self.x, 10*self.y, 10, 10)
        pygame.draw.rect(screen, colour, rect)

    def rand():
        return Box(random.randrange(BOARD_SIZE), random.randrange(BOARD_SIZE))

class Food(Box):
    def __init__(self, snake):
        self.move(snake)

    def draw(self, screen):
        # Draw the food to the screen
        Box.draw(self, screen, RED)

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

    def move(self, food):
        # Move the snake up, down, left, or right
        new_dir = get_input()
        if new_dir[0] != -1 * self.dir[0] and new_dir[1] != -1 * self.dir[1] and new_dir != (0, 0):
            # Change move direction
            self.dir = new_dir
        new_head = self.head + self.dir

        if new_head in self.body[:-1] or -1 in new_head.coords or BOARD_SIZE in new_head.coords:
            # Collision
            self.alive = False

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

    def draw(self, screen):
        # Draw the snake to the display surface
        self.head.draw(screen, WHITE)
        for box in self.body:
            draw_box(screen, box, GREY)

# Helper functions ---------------

# Get input from human or neural net
def get_input():
    if HUMAN_PLAYER:
        # Check if arrow keys were pressed
        pass
    else:
        # Run neural net
        pass
    return (0, 0)

# Reset game after game over
def reset_game():
    global snek, apple
    random.seed(SEED)
    snek = Snake()
    apple = Food(snek)

# Fill the screen black
def clear_screen(screen):
    screen.fill(BLACK)

# Setup --------------------------

if SHOW_BOARD:
    pygame.init()
    screen = pygame.display.set_mode((BOARD_SIZE*10, BOARD_SIZE*10))
    pygame.display.set_caption("Snake game")
    clock = pygame.time.Clock()

reset_game()

# Main game loop -----------------

while True:
    if snek.isAlive == True:
        snek.move(apple)

    if SHOW_BOARD:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        clear_screen(screen)
        snek.draw(screen)
        apple.draw(screen)

        pygame.display.update()
        clock.tick(FPS)