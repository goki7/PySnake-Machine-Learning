from random import randint, randrange
import pygame as pg
import numpy as np

vec2 = pg.math.Vector2

class SnakeAI:
    def __init__(self, game):
        self.game = game
        self.size = game.TILE_SIZE
        self.rect = pg.rect.Rect([0, 0, game.TILE_SIZE - 2, game.TILE_SIZE - 2])
        self.rect.center = self.get_random_position()
        self.direction = randint(1,4)
        self.movement = vec2(0, 0)
        self.step_delay = 1 # milliseconds
        self.time = 0
        self.length = 1
        self.body = [self.rect.copy()]
        self.UP, self.DOWN = vec2(0, -self.size), vec2(0, self.size)
        self.RIGHT, self.LEFT = vec2(-self.size, 0), vec2(self.size, 0)
        self.right, self.left = 1, 2
        self.up, self.down = 3, 4
        #self.directions = {pg.K_w: 1, pg.K_s: 1, pg.K_a: 1, pg.K_d: 1}

    def is_collision(self, pt):
        # hits boundary
        if pt[0] > (self.game.WIN_SIZE - self.game.TILE_SIZE-2) or pt[0] < 0 or pt[1] > (self.game.WIN_SIZE  - self.game.TILE_SIZE-2) or pt[1] < 0 or self.game.iteration > 100 * len(self.body):
            return True

        segments = set(segment.center for segment in self.body)
        if len(segments) > 2:
            if (pt[0] + 23, pt[1]) in segments:
                #print("Danger Left")
                return True
            if (pt[0] - 23, pt[1]) in segments:
                #print("Danger Right")
                return True
            if (pt[0], pt[1] - 23) in segments:
                #print("Danger Up")
                return True
            if (pt[0], pt[1] + 23) in segments:
                #print("Danger Down")
                return True
                
        return False

    def delta_time(self):
        time_now = pg.time.get_ticks()
        if time_now - self.time > self.step_delay:
            self.time = time_now
            return True
        return False 

    def controlAI(self, action):
        # AI input movement logic with just numbers, then converted in vec2() visual position
        clockwise = [self.right, self.down, self.left, self.up]  # directions RIGHT, DOWN, LEFT, UP
        current_direction = clockwise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_direction = clockwise[current_direction] # no change in direction
        elif np.array_equal(action, [0, 1, 0]):
            next_current_direction = (current_direction + 1) % 4
            new_direction = clockwise[next_current_direction] # right turn r -> d -> l -> u
        else: # [0, 0, 1]
            next_current_direction = (current_direction - 1) % 4
            new_direction = clockwise[next_current_direction] # left turn r -> u -> l -> d
        
        self.direction = new_direction

        if self.direction == self.right:
            self.movement = self.RIGHT
    
        if self.direction == self.left:
            self.movement = self.LEFT
        
        if self.direction == self.up:
            self.movement = self.UP
        
        if self.direction == self.down:
            self.movement = self.DOWN

        self.move()
    
    def move(self):
        #if self.delta_time():
        self.rect.move_ip(self.movement)
        self.body.append(self.rect.copy())
        self.body = self.body[-self.length:]

    def get_random_position(self):
        return [randrange(self.size // 2, self.game.WIN_SIZE - self.size // 2, self.size)] * 2

    def check_borders(self):
        if self.rect.left < 0 or self.rect.right > self.game.WIN_SIZE or self.game.iteration > 100 * len(self.body):
            self.game.game_over = True
            self.game.reward = -100
            return self.game.reward, self.game.game_over, self.game.score

        if self.rect.top < 0 or self.rect.bottom > self.game.WIN_SIZE or self.game.iteration > 100 * len(self.body):
            self.game.game_over = True
            self.game.reward = -100
            return self.game.reward, self.game.game_over, self.game.score

    def check_food(self):
        # if snake and food intersect, spawn new food randomly
        if self.rect.center == self.game.food.rect.center:
            self.game.food.rect.center = self.get_random_position()

            # spawn new apple avoiding to position it within the snake's body
            while self.game.food.rect.center in [segment.center for segment in self.body]:
                #print("spawn error")
                self.game.food.rect.center = self.get_random_position()
                
            self.length += 1
            self.game.score += 1
            #self.game.score_text = self.game.font.render(f"SCORE: {self.game.score}", True, (255, 255, 255))
            self.game.reward = 150

    def check_cannibalism(self):
        if len(self.body) != len(set(segment.center for segment in self.body)) or self.game.iteration > 100 * len(self.body):
            self.game.game_over = True
            self.game.reward = -100
            return self.game.reward, self.game.game_over, self.game.score

    def draw(self):
        pg.draw.rect(self.game.screen, "blue", self.body[0])
        if len(self.body) > 1:
            [pg.draw.rect(self.game.screen, "green", segment) for segment in self.body]
            pg.draw.rect(self.game.screen, "blue", self.body[-1])

class Food:
    def __init__(self, game):
        self.game = game
        self.size = game.TILE_SIZE
        self.rect = pg.rect.Rect([0, 0, game.TILE_SIZE - 2, game.TILE_SIZE - 2])
        
        self.rect.center = self.game.snake.get_random_position()
        while self.rect.center in [segment.center for segment in self.game.snake.body]:
            self.rect.center = self.game.snake.get_random_position()
            #print("WRONG SPAWN SITE")

    def draw(self):
        pg.draw.rect(self.game.screen, "red", self.rect)

        """
        segments = set(segment.center for segment in self.body)
        if len(segments) > 2:
            if (pt[0] + 23, pt[1]) in segments:
                print("Danger Left")
                return True
            if (pt[0] - 23, pt[1]) in segments:
                print("Danger Right")
                return True
            if (pt[0], pt[1] - 23) in segments:
                print("Danger Up")
                return True
            if (pt[0], pt[1] + 23) in segments:
                print("Danger Down")
                return True
"""