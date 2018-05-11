import pygame, sys, random
from pygame.locals import *
import network

# Colours ----------------------------------------------------------------------

WHITE      = (255,255,255)
GREY       = (127,127,127)
BLACK      = (  0,  0,  0)
RED        = (255,  0,  0)
LIGHT_BLUE = (109,158,237)

# Game settings ----------------------------------------------------------------

HUMAN_PLAYER  = False
SHOW_BOARD    = True
BOARD_SIZE    = 16
BOX_SIZE      = 20
HUD_HEIGHT    = 40
HUD_COLOUR    = LIGHT_BLUE
TEXT_SIZE     = 30
TEXT_COLOUR   = BLACK
BORDER_WIDTH  = 5
BORDER_COLOUR = WHITE
FPS           = 30
SNAKE_SPEED   = 10
GAME_SEED     = 2

# Network settings -------------------------------------------------------------

NUM_NETWORKS    = 100
MAX_AGE         = 100
DOMINATION_RATE = 0.99
MUTATION_RATE   = 0.01
HIDDEN_LAYERS   = 1
HIDDEN_NODES    = 8
NETWORK_SEED    = 2
LOAD_NETWORK    = True
INPUT_FILE      = "log.txt"
OUTPUT_FILE     = "log.txt"

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
        self.is_alive = True
        self.length = 1
        self.dir = UP
        if not HUMAN_PLAYER and MAX_AGE > 0:
            self.age = 0

    def _set_dir(self, food):
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
            output = AI.run(self.network_inputs(food))
            decision = output.index(max(output)) - 1
            # -1 -> left turn, 0 -> forward, 1 -> right turn
            directions = [UP, RIGHT, DOWN, LEFT]
            self.dir = directions[(directions.index(self.dir) + decision) % 4]

    def move(self, food):
        # Move the snake up, down, left, or right
        self._set_dir(food)
        new_head = self.head + self.dir

        if new_head in self.body[:-1] or -1 in new_head.coords or BOARD_SIZE in new_head.coords:
            # Collision
            self.is_alive = False

        elif new_head == food:
            # Grow snake
            self.length += 1
            self.body.append(self.head)
            self.head = new_head
            food.move(self)
            if not HUMAN_PLAYER and MAX_AGE > 0:
                self.age = 0

        else:
            # Move snake
            self.body.append(self.head)
            self.head = new_head
            del self.body[0]
            if not HUMAN_PLAYER and MAX_AGE > 0:
                self.age += 1
                if self.age > MAX_AGE:
                    self.is_alive = False

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

        return [forward, left, right, food_side, food_front]


# Helper functions -------------------------------------------------------------

# Reset game after game over
def reset_game():
    global snek, apple
    random.seed(GAME_SEED)
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
                    global last_press
                    last_press = K_UP
                    restart = True
            pygame.display.update()
            clock.tick(FPS)

    else:
        score = snek.length + 1.0/float(abs(snek.head.x-apple.x) + abs(snek.head.y-apple.y))
        if SHOW_BOARD:
            print("Generation:", AI.generation, "   Network number:", AI.curr_network+1, "   Score:", score)
        elif AI.curr_network == 0:
            print("Generation:", AI.generation, "   Score:", score)
        AI.next(score)

    reset_game()

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
else:
    # Set up neural networks
    if LOAD_NETWORK:
        AI = network.Species(True, NUM_NETWORKS, DOMINATION_RATE, MUTATION_RATE, INPUT_FILE, OUTPUT_FILE)
    else:
        AI = network.Species(False, NUM_NETWORKS, DOMINATION_RATE, MUTATION_RATE, 5, 3, HIDDEN_LAYERS, HIDDEN_NODES, "rand", NETWORK_SEED, OUTPUT_FILE)

    # (self, num_networks, domination_rate, mutation_rate, activation, inputs, outputs,
    # hidden_layers, hidden_nodes=0, initialization="rand", seed=None, output_file=None)

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
            if snek.is_alive:
                snek.move(apple)
            else:
                game_over()
            # Update display
            update_hud(snek)
            game_board.fill(BLACK)
            snek.draw(game_board)
            apple.draw(game_board)
            screen.blit(hud, (0, 0))
            screen.blit(game_board, (BORDER_WIDTH, HUD_HEIGHT+BORDER_WIDTH))
            pygame.display.update()

        clock.tick(FPS)
        count_frames += 1

    else: # Hidden board
        if snek.is_alive:
            snek.move(apple)
        else:
            game_over()