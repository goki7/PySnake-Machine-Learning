import torch
import numpy as np
from Game import Game
from model import Linear_QNet

class Trained_AI:
    def __init__(self):
        self.number_games = 0

        # Load state dict of trained model
        self.model = Linear_QNet(11, 256, 3)
        self.model.load_state_dict(torch.load("./model/model.pth"))

    def get_state(self, game):
        head = game.snake.rect.center
        
        point_l = (head[0] - 23, head[1])
        point_r = (head[0] + 23, head[1])
        point_u = (head[0], head[1] - 23)
        point_d = (head[0], head[1] + 23)

        #print(f"Head: {head}, Left: {point_l}, Right: {point_r}, Up: {point_u}, Down: {point_d}")
        #print(f"Head: {head}, Left: {head[0] - 23}, Right: {head[0] + 23}, Up: {head[1] - 23}, Down: {head[1] + 23}")
        #exit()
        dir_l = game.snake.direction == game.snake.left
        dir_r = game.snake.direction == game.snake.right
        dir_u = game.snake.direction == game.snake.up
        dir_d = game.snake.direction == game.snake.down

        state = [
            # Danger straight
            (dir_r and game.snake.is_collision(point_r)) or 
            (dir_l and game.snake.is_collision(point_l)) or 
            (dir_u and game.snake.is_collision(point_u)) or 
            (dir_d and game.snake.is_collision(point_d)),

            # Danger right
            (dir_u and game.snake.is_collision(point_r)) or 
            (dir_d and game.snake.is_collision(point_l)) or 
            (dir_l and game.snake.is_collision(point_u)) or 
            (dir_r and game.snake.is_collision(point_d)),

            # Danger left
            (dir_d and game.snake.is_collision(point_r)) or 
            (dir_u and game.snake.is_collision(point_l)) or 
            (dir_r and game.snake.is_collision(point_u)) or 
            (dir_l and game.snake.is_collision(point_d)),
            
            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            
            # Food location 
            game.food.rect.left < game.snake.rect.left,  # food left
            game.food.rect.right > game.snake.rect.right,  # food right
            game.food.rect.top < game.snake.rect.top,  # food up
            game.food.rect.bottom > game.snake.rect.bottom  # food down
            ]
        #print(f"Left: {game.food.rect.left < game.snake.rect.left}, Right: { game.food.rect.right > game.snake.rect.right}, Up: {game.food.rect.top < game.snake.rect.top}, Down: {game.food.rect.bottom > game.snake.rect.bottom}")
        #print(f"Left: {game.food.rect.left < game.snake.rect.left}, Right: { game.food.rect.right > game.snake.rect.right}, Up: {game.food.rect.top < game.snake.rect.top}, Down: {game.food.rect.bottom > game.snake.rect.bottom}")
        return np.array(state, dtype=int)

    def get_action(self, state):
        final_move = [0, 0, 0]
        state0 = torch.tensor(state, dtype=torch.float)
        prediction = self.model(state0)
        move = torch.argmax(prediction).item()
        final_move[move] = 1

        return final_move

def play():
    ai = Trained_AI()
    game = Game()

    while True:
        current_state = ai.get_state(game)

        # get move
        final_move = ai.get_action(current_state)

        # perform move and get new state
        _ , done, _ = game.update(final_move)

        if done:
            game.defeat()
            # TODO: implement defeat() method

if __name__ == "__main__":
    play()