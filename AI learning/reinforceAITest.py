import random
import numpy as np

class simpleGridWorld():
    def __init__(self):
        self.x = 0
        self.y = 0

    def step(self, a):
        if a == 0:
            self.moveLeft()
        elif a == 1:
            self.moveUp()
        elif a == 2:
            self.moveRight()
        elif a == 3:
            self.moveDown()

        reward = -1
        done = self.isDone()
        return (self.x, self.y), reward, done

    def moveRight(self):
        self.y += 1
        if self.y > 3:
            self.y = 3

    def moveLeft(self):
        self.y -= 1
        if self.y < 0:
            self.y = 0

    def moveUp(self):
        self.x -= 1
        if self.x < 0:
            self.x = 0

    def moveDown(self):
        self.x += 1
        if self.x > 3:
            self.x = 3

    def isDone(self):
        if self.x == 3 and self.y == 3:
            return True
        else:
            return False

    def getState(self):
        return (self.x, self.y)

    def reset(self):
        self.x = 0
        self.y = 0
        return (self.x, self.y)


class Agent():
    def __init__(self):
        pass
    
    def selectAction(self):
        return random.randint(0, 3)

    
class GridWorld():
    def __init__(self):
        self.x = 0
        self.y = 0

    def step(self, a):
        if a == 0:
            self.moveLeft()
        elif a == 1:
            self.moveUp()
        elif a == 2:
            self.moveRight()
        elif a == 3:
            self.moveDown()

        reward = -1
        done = self.isDone()
        return (self.x, self.y), reward, done

    def moveRight(self):
        if self.y == 6:
            pass
        elif self.y == 1 and self.x in [0, 1, 2]:
            pass
        elif self.y == 3 and self.x in [2, 3, 4]:
            pass
        else:
            self.y += 1

    def moveLeft(self):
        if self.y == 0:
            pass
        elif self.y == 3 and self.x in [0, 1, 2]:
            pass
        elif self.y == 5 and self.x in [2, 3, 4]:
            pass
        else:
            self.y -= 1

    def moveUp(self):
        if self.x == 0:
            pass
        elif self.x == 3 and self.y == 2:
            pass
        else:
            self.x -= 1

    def moveDown(self):
        if self.x == 4:
            pass
        elif self.x == 1 and self.y == 4:
            pass
        else:
            self.x += 1

    def isDone(self):
        if self.x == 4 and self.y == 6:
            return True
        else:
            return False

    def reset(self):
        self.x = 0
        self.y = 0
        return (self.x, self.y)


class QAgent():
    def __init__(self):
        self.q_table = np.zeros((5, 7, 4))
        self.eps = 0.9
        self.alpha = 0.01
        self.gamma = 1

    def selectAction(self, s):
        x, y = s
        coin = random.random()
        if coin < self.eps:
            action = random.randint(0, 3)
        else:
            action_val = self.q_table[x, y, :]
            action = np.argmax(action_val)
        return action

    def updateTableByMC(self, history):
        cum_reward = 0
        for transition in history[::-1]:
            s, a, r, s_prime = transition
            x, y = s
        
            self.q_table[x, y, a] = self.q_table[x, y, a] + 0.1*(cum_reward - self.q_table[x, y, a])
            cum_reward = self.gamma*cum_reward + r
            
    # SARSA: calculate the Q value of state-action pair using the Q value of next state-action pair
    def updateTableByTD(self, transition):
        s, a, r, s_prime = transition
        x, y = s
        next_x, next_y = s_prime
        a_prime = self.selectAction(s_prime)
        
        self.q_table[x, y, a] = self.q_table[x, y, a] + 0.1*(r + self.q_table[next_x, next_y, a_prime] - self.q_table[x, y, a])
    
    # QLearning: calculate the Q value of state-action pair using the maximum Q value of next state-action pair
    def updateTableByQL(self, transition):
        s, a, r, s_prime = transition
        x, y = s
        next_x, next_y = s_prime
        
        self.q_table[x, y, a] = self.q_table[x, y, a] + 0.1*(r + np.amax(self.q_table[next_x, next_y,:]) - self.q_table[x, y, a])
    
    def anneal_eps(self):
        self.eps -= 0.03
        self.eps = max(self.eps, 0.1)

    def anneal_epsByQL(self):
        self.eps -= 0.01
        self.eps = max(self.eps, 0.2)
        
    def showTable(self):
        q_list = self.q_table.tolist()
        data = np.zeros((5, 7))
        for row_idx in range(len(q_list)):
            row = q_list[row_idx]
            for col_idx in range(len(row)):
                col = row[col_idx]
                action = np.argmax(col)
                data[row_idx, col_idx] = action
        print(data)
        print()

# ================================ prediction state value function ================================ #    

def monteCarlo_V():
    env = simpleGridWorld()
    agent = Agent()
    
    # initailize the table
    data = [[0, 0, 0, 0],[0, 0, 0, 0],[0, 0, 0, 0],[0, 0, 0, 0]]
    gamma = 1.0
    alpha = 0.0001
    
    # learning 50000 episodes
    for k in range(50000):
        done = False
        history = []
        
        # create episode
        while not done:
            action = agent.selectAction()
            (x, y), reward, done = env.step(action)
            history.append((x, y, reward))
            
        # update the table
        cum_reward = 0
        for transition in history[::-1]:
            x, y, reward = transition
            data[x][y] = data[x][y] + alpha*(cum_reward - data[x][y])
            cum_reward = cum_reward + gamma*reward
            
        env.reset()
    
    # print results
    for row in data:
        print(row)
        
        
def tempDiff_V():
    env = simpleGridWorld()
    agent = Agent()
    
    # initailize the table
    data = [[0, 0, 0, 0],[0, 0, 0, 0],[0, 0, 0, 0],[0, 0, 0, 0]]
    gamma = 1.0
    alpha = 0.01
    
    # learning 50000 episodes
    for k in range(50000):
        done = False
        while not done:
            x, y = env.getState()
            action = agent.selectAction()
            (next_x, next_y), reward, done = env.step(action)
            data[x][y] = data[x][y] + alpha*(reward + gamma*data[next_x][next_y] - data[x][y])
            
        env.reset()
    
    # print results
    for row in data:
        print(row)        

# ================================ Control action value function ================================ #    

def monteCarlo_Q():
    env = GridWorld()
    agent = QAgent()
    
    for n_epi in range(10000):
        done = False
        history = []
        
        s = env.reset()
        while not done:
            a = agent.selectAction(s)
            s_prime, r, done = env.step(a)
            history.append((s, a, r, s_prime))
            s = s_prime
        
        agent.updateTableByMC(history)
        agent.anneal_eps()
    
    agent.showTable()
    
def SARSA_Q():
    env = GridWorld()
    agent = QAgent()
    
    for _ in range(10000):
        done = False
        
        s = env.reset()
        while not done:
            a = agent.selectAction(s)
            s_prime, r, done = env.step(a)
            agent.updateTableByTD((s, a, r, s_prime))
            s = s_prime
        
        agent.anneal_eps()
    
    agent.showTable()

def QLearning():
    env = GridWorld()
    agent = QAgent()
    
    for _ in range(10000):
        done = False
        
        s = env.reset()
        while not done:
            a = agent.selectAction(s)
            s_prime, r, done = env.step(a)
            agent.updateTableByQL((s, a, r, s_prime))
            s = s_prime
        
        agent.anneal_epsByQL()
    
    agent.showTable()

# ================ main ================ #
        
if __name__ == '__main__':
    print(f'monteCarlo_V :')
    monteCarlo_V()
    print(f'tempDiff_V :')
    tempDiff_V()
    print(f'monteCarlo_Q :')
    monteCarlo_Q()
    print(f'SARSA_Q :')
    SARSA_Q()
    print(f'QLearning :')
    QLearning()
    