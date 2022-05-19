import torch
import random
import numpy as np
from collections import deque
from Game import Game
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100000
BATCH_SIZE = 1000
LR = 0.0002

class Agent:
    def __init__(self):
        self.number_games = 0
        self.epsilon = 0  # parameter to control randomness
        self.gamma = 0.9   # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft() if memory exceded
        self.model = Linear_QNet(11, 256, 3)
        
        # load trained model
        self.model.load_state_dict(torch.load("./model/model.pth"))
        self.model.eval()
        
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

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

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_term(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)  # List of tuples
        else:
            mini_sample = self.memory
        
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_term(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.number_games
        final_move = [0, 0, 0]

        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = Game()

    while True:
        # get current state
        current_state = agent.get_state(game)

        # get move
        final_move = agent.get_action(current_state)

        # perform move and get new state
        reward, done, score = game.update(final_move)
        new_state = agent.get_state(game)

        # train short memory
        agent.train_short_term(current_state, final_move, reward, new_state, done)

        # remember
        agent.remember(current_state, final_move, reward, new_state, done)

        if done:
            # train long term memory, plot result
            game.reset()
            agent.number_games += 1
            agent.train_long_term()

            if score > record:
                record = score
                agent.model.save()
            
            #print(f"Game: {agent.number_games}, Score: {score}, Record: {record}")

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.number_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

if __name__ == "__main__":
    train()