import pygame as pg
from Snake import *

class Game:
    def __init__(self):
        pg.init()
        pg.display.set_caption("SnakeAI")
        self.WIN_SIZE = 750
        self.TILE_SIZE = 25
        #self.screen = pg.display.set_mode([self.WIN_SIZE] * 2)
        self.clock = pg.time.Clock()
        self.FPS = 100000
        self.grid_color = [50, 50, 50] #rgb
        self.game_over = False
        self.score = 0
        #self.font = pg.font.SysFont(None, 48)
        self.reset()

    def draw_grid(self):
        # draws grid, line by line, for each axis
        [pg.draw.line(self.screen, self.grid_color, (x, 0), (x, self.WIN_SIZE)) for x in range(0, self.WIN_SIZE, self.TILE_SIZE)]
        [pg.draw.line(self.screen, self.grid_color, (0, y), (self.WIN_SIZE, y)) for y in range(0, self.WIN_SIZE, self.TILE_SIZE)]        
    
    def reset(self):
        self.score = 0
        self.iteration = 0
        #self.score_text = self.font.render(f"SCORE: {self.score}", True, (255, 255, 255))
        self.snake = SnakeAI(self)
        self.food = Food(self)
        self.snake.direction = self.snake.right

    def update(self, action):
        self.iteration += 1

        # user input
        #for event in pg.event.get():
        #    if event.type == pg.QUIT:
        #        pg.quit()
        #        quit()

        # move
        self.snake.controlAI(action)

        # check game over
        self.reward = 0
        self.game_over = False
        self.snake.check_borders() 
        self.snake.check_cannibalism()

        # check collision with food
        self.snake.check_food()

        # update screen and clock
        #self.draw()

        #print(self.iteration)
        self.clock.tick(self.FPS)

        return self.reward, self.game_over, self.score

    def draw(self):
        self.screen.fill("black")
        self.draw_grid()
        self.food.draw()
        self.snake.draw()
        self.screen.blit(self.score_text, (30, 50))
        pg.display.flip()
    
    def defeat(self):
        self.screen.fill("black")
        self.screen.blit(self.font.render("GAME OVER", True, (255, 255, 255)), (375, 375))
        pg.display.flip()