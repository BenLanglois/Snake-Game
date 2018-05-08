import pygame, sys, random
from pygame.locals import *

# Colours ----------------------------------------------------------------------

WHITE      = (255,255,255)
GREY       = (127,127,127)
BLACK      = (  0,  0,  0)
RED        = (255,  0,  0)
LIGHT_BLUE = (109,158,237)

# Settings ---------------------------------------------------------------------

HUMAN_PLAYER  = True
SHOW_BOARD    = True
BOARD_SIZE    = 32
BOX_SIZE      = 20
HUD_HEIGHT    = 40
HUD_COLOUR    = LIGHT_BLUE
TEXT_SIZE     = 30
TEXT_COLOUR   = BLACK
BORDER_WIDTH  = 5
BORDER_COLOUR = WHITE
FPS           = 30
SNAKE_SPEED   = 10
SEED          = 1

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
        if type(other) == Direction:
            return Box(self.x + other.x, self.y + other.y)
        else:
            return NotImplemented

    def __sub__(self, other):
        if type(other) == Direction:
            return Box(self.x - other.x, self.y - other.y)
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

class Direction:
    def __init__(self, x, y):
        self.x, self.y = x, y


class Snake:
    def __init__(self):
        self.head = Box(BOARD_SIZE//2, BOARD_SIZE//2)
        self.body = []
        self.isAlive = True
        self.length = 1
        self.dir = UP

    def _set_dir(self):
        if HUMAN_PLAYER:
            if last_press == K_UP:
                if self.dir != DOWN: self.dir = UP
            elif last_press == K_DOWN:
                if self.dir != UP: self.dir = DOWN
            elif last_press == K_LEFT:
                if self.dir != RIGHT: self.dir = LEFT
            elif last_press == K_RIGHT:
                if self.dir != LEFT: self.dir = RIGHT
        else:
            # Run neural net
            pass

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

    def _dist_to_obstacle(self, dir):
        cursor = self.head
        cursor += dir
        count = 1
        while cursor not in self.body and cursor.x >= 0 and cursor.x < BOARD_SIZE and cursor.y >= 0 and cursor.y < BOARD_SIZE:
            # Move cursor until it hits an obstacle
            count += 1
            cursor += dir
        return count

    def network_inputs(self, food):
        # Returns neural net inputs in a dict
        directions = [UP, RIGHT, DOWN, LEFT]
        forward = self._dist_to_obstacle(self.dir)
        left = self._dist_to_obstacle(directions[(directions.index(self.dir)-1)%4])
        right = self._dist_to_obstacle(directions[(directions.index(self.dir)+1)%4])

        if self.dir == UP:
            food_side = food.x - self.head.x
            food_front = self.head.y - food.y
        elif self.dir == DOWN:
            food_side = self.head.x - food.x
            food_front = food.y - self.head.y
        elif self.dir == LEFT:
            food_side = self.head.y - food.y
            food_front = self.head.x - food.x
        elif self.dir == RIGHT:
            food_side = food.y - self.head.y
            food_front = food.x - self.head.x

        return {"forward": forward, "left": left, "right": right, "food side": food_side, "food front": food_front}


# Helper functions -------------------------------------------------------------

# Reset game after game over
def reset_game():
    global snek, apple
    random.seed(SEED)
    snek = Snake()
    apple = Food(snek)

# Snake died, restart game
def game_over():
    if HUMAN_PLAYER:
        death_screen_surf = pygame.Surface((BOARD_SIZE*BOX_SIZE/2, BOARD_SIZE*BOX_SIZE/2))
        death_screen_surf.fill(HUD_COLOUR)
        death_screen_rect = death_screen_surf.get_rect()
        death_text_surf = hud_font.render("Press space to restart", True, TEXT_COLOUR)
        death_text_rect = death_text_surf.get_rect()
        death_text_rect.center = death_screen_rect.center
        death_screen_surf.blit(death_text_surf, death_text_rect)
        death_screen_rect.center = game_board.get_rect().center
        game_board.blit(death_screen_surf, death_screen_rect)
        screen.blit(game_board, (BORDER_WIDTH, HUD_HEIGHT+BORDER_WIDTH))
        pygame.display.update()

        restart = False
        while not restart:
            for event in pygame.event.get():
                if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN and event.key == K_SPACE:
                    reset_game()
                    global last_press
                    last_press = K_UP
                    restart = True
            pygame.display.update()
            clock.tick(FPS)

    else:
        pass

def update_hud(snake):
    hud.fill(HUD_COLOUR)
    score_text_surf = hud_font.render("SCORE: " + str(snake.length), True, TEXT_COLOUR)
    score_text_rect = score_text_surf.get_rect()
    score_text_rect.center = (BOARD_SIZE*BOX_SIZE/2, HUD_HEIGHT/2)
    hud.blit(score_text_surf, score_text_rect)


# Setup ------------------------------------------------------------------------

SHOW_BOARD = HUMAN_PLAYER or SHOW_BOARD # Must SHOW_BOARD if HUMAN_PLAYER

# Directions
UP = Direction(0, -1)
DOWN = Direction(0, 1)
LEFT = Direction(-1, 0)
RIGHT = Direction(1, 0)

if SHOW_BOARD:
    pygame.init()
    # Surfaces
    screen = pygame.display.set_mode((BOARD_SIZE*BOX_SIZE+BORDER_WIDTH*2, BOARD_SIZE*BOX_SIZE+HUD_HEIGHT+BORDER_WIDTH*2))
    screen.fill(BORDER_COLOUR)
    pygame.display.set_caption("Snake game")
    game_board = pygame.Surface((BOARD_SIZE*BOX_SIZE, BOARD_SIZE*BOX_SIZE))
    hud = pygame.Surface((BOARD_SIZE*BOX_SIZE+BORDER_WIDTH*2, HUD_HEIGHT))
    hud_font = pygame.font.SysFont("Verdana", TEXT_SIZE)
    # Clock related
    clock = pygame.time.Clock()
    skip_frames = FPS/SNAKE_SPEED
    count_frames = 0
    # Other
    if HUMAN_PLAYER:
        last_press = K_UP

reset_game()

# Main game loop ---------------------------------------------------------------

while True:
    if SHOW_BOARD:
        # Receive user input
        for event in pygame.event.get():
            if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif HUMAN_PLAYER and event.type == KEYDOWN and event.key in (K_UP, K_DOWN, K_LEFT, K_RIGHT):
                last_press = event.key

    if count_frames >= skip_frames:
        count_frames -= skip_frames

        # Run game logic
        if snek.isAlive:
            snek.move(apple)
        else:
            game_over()

        if SHOW_BOARD:
            update_hud(snek)
            game_board.fill(BLACK)
            snek.draw(game_board)
            apple.draw(game_board)

            screen.blit(hud, (0, 0))
            screen.blit(game_board, (BORDER_WIDTH, HUD_HEIGHT+BORDER_WIDTH))

            pygame.display.update()

    if SHOW_BOARD:
        clock.tick(FPS)
        count_frames += 1