#
import time

# for DQN testing
import gymnasium as gym
import collections
import random

#
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from torch.distributions import Categorical

import numpy as np
import matplotlib.pyplot as plt

# Hyperparameters
DQN_learning_rate = 0.0005
REINF_learning_rate = 0.0002
TDAC_learning_rate = 0.0002

gamma = 0.98
buffer_limit = 50000
batch_size = 32
scoring_limitTimeout = 10
n_rollout = 10

goal = 3

# troubleshooting
np.bool8 = np.bool

# ================ NNtest ================ #

# NN module
class Model(nn.Module):
    def __init__(self):
        super(Model, self).__init__()
        self.fc1 = nn.Linear(1, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, 128)
        self.fc4 = nn.Linear(128, 1, bias=False)
        
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = self.fc4(x)
        return x
    
# true data generation function
def true_fun(X):
    noise = np.random.rand(X.shape[0]) * 0.4 - 0.2
    return np.cos(1.5 * np.pi * X) + X + noise

# plotting
def plot_results(model):
    x = np.linspace(0, 5, 100)
    input_x = torch.from_numpy(x).float().unsqueeze(1)
    
    plt.plot(x, true_fun(x), label='Truth')
    plt.plot(x, model(input_x).detach().numpy(), label='Prediction')
    plt.legend(loc='lower right', fontsize=15)
    plt.xlim((0, 5))
    plt.ylim((-1, 5))
    plt.grid()
    plt.show()
    
def NNtest():
    # sampling 10000 num([0, 5])
    data_x = np.random.rand(10000) * 5
    model = Model()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    for step in range(10000):
        # mini-batch
        batch_x = np.random.choice(data_x, 32)
        batch_x_tensor = torch.from_numpy(batch_x).float().unsqueeze(1)
        pred = model(batch_x_tensor)
        
        batch_y = true_fun(batch_x)
        truth = torch.from_numpy(batch_y).float().unsqueeze(1)
        # calculate MSE
        loss = F.mse_loss(pred, truth)
        
        optimizer.zero_grad()
        # backpropagation
        loss.mean().backward()
        # update the weights
        optimizer.step()
        
    plot_results(model)

# ================ DQN ================ #

class ReplayBuffer():
    def __init__(self):
        self.buffer = collections.deque(maxlen=buffer_limit)
        
    def put(self, transition):
        self.buffer.append(transition)
        
    def sample(self, n):
        mini_batch = random.sample(self.buffer, n)
        s_lst, a_lst, r_lst, s_prime_lst, done_mask_lst = [], [], [], [], []
        
        for transition in mini_batch:
            s, a, r, s_prime, done_mask = transition
            s_lst.append(s)
            a_lst.append([a])
            r_lst.append([r])
            s_prime_lst.append(s_prime)
            done_mask_lst.append([done_mask])
            
        return torch.tensor(np.array(s_lst), dtype=torch.float), torch.tensor(np.array(a_lst)), \
            torch.tensor(np.array(r_lst)), torch.tensor(np.array(s_prime_lst), dtype=torch.float), \
            torch.tensor(np.array(done_mask_lst))
        
    def size(self):
        return len(self.buffer)

class Qnet(nn.Module):
    def __init__(self):
        super(Qnet, self).__init__()
        self.fc1 = nn.Linear(4, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, 2)
        
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x
    
    def sample_action(self, obs, epsilon):
        out = self.forward(obs)
        coin = random.random()
        if coin < epsilon:
            return random.randint(0, 1)
        else:
            return out.argmax().item()

def train(q, q_target, memory, optimizer):
    for i in range(10):
        s, a, r, s_prime, done_mask = memory.sample(batch_size)
        
        q_out = q(s)
        q_a = q_out.gather(1, a)
        max_q_prime = q_target(s_prime).max(1)[0].unsqueeze(1)
        target = r + gamma * max_q_prime * done_mask
        
        loss = F.smooth_l1_loss(q_a, target)
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

def DQNtest():
    env = gym.make('CartPole-v1')
    q = Qnet()
    q_target = Qnet()
    q_target.load_state_dict(q.state_dict())
    memory = ReplayBuffer()
    
    print_interval = 20
    score = 0.0
    optimizer = optim.Adam(q.parameters(), lr=DQN_learning_rate)
    
    timeLapse = 0
    
    for n_epi in range(10000):
        startTime = time.time()
        epsilon = max(0.01, 0.08 - 0.01*(n_epi/200))
        s, _ = env.reset()
        done = False
        
        while not done:
            a = q.sample_action(torch.from_numpy(s).float(), epsilon)
            s_prime, r, done, _, info = env.step(a)
            done_mask = 0.0 if done else 1.0
            memory.put((s, a, r/1000.0, s_prime, done_mask))
            s = s_prime
            
            score += r
            if done or time.time() > startTime + scoring_limitTimeout:
                break
            
        print("time : ", time.time() - startTime, "scoring result")
        timeLapse += time.time() - startTime
        
        if memory.size() > 2000:
            train(q, q_target, memory, optimizer)
         
        if n_epi % print_interval == 0 and n_epi != 0:
            q_target.load_state_dict(q.state_dict())
            print("timeLapse : ", timeLapse)
            print("n_episode : {}, score : {:.1f}, n_buffer : {}, eps : {:.1f}%".format(
                n_epi, score/print_interval, memory.size(), epsilon*100))
            score = 0.0
            
            if timeLapse > goal*print_interval:
                print(__name__, "goal reached at episode : ", n_epi)
                break
            timeLapse = 0
            
            
    env.close()

# ================ REINFORCE ================ #

class Policy(nn.Module):
    def __init__(self):
        super(Policy, self).__init__()
        self.data = []
        
        self.fc1 = nn.Linear(4, 128)
        self.fc2 = nn.Linear(128, 2)
        self.optimizer = optim.Adam(self.parameters(), lr=REINF_learning_rate)
        
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.softmax(self.fc2(x), dim=0)
        return x
    
    def put_data(self, transition):
        self.data.append(transition)
        
    def train_net(self):
        R = 0
        self.optimizer.zero_grad()
            
        for r, prob in self.data[::-1]:
            R = r + gamma * R
            loss = -torch.log(prob) * R
            loss.backward()
            
        self.optimizer.step()
        self.data = []

def REINFORCE():
    env = gym.make('CartPole-v1')
    pi = Policy()
    
    score = 0.0
    print_interval = 20
    
    timeLapse = 0
    
    for n_epi in range(10000):
        s, _ = env.reset()
        done = False
        
        startTime = time.time()
        
        while not done:
            prob = pi(torch.from_numpy(s).float())
            m = Categorical(prob)
            a = m.sample().item()
            s_prime, r, done, _, info = env.step(a)
            pi.put_data((r, prob[a]))
            s = s_prime
            score += r
            
            if done or time.time() > startTime + scoring_limitTimeout:
                break
     
        print("time : ", time.time() - startTime, "scoring result")
        timeLapse += time.time() - startTime

        pi.train_net()
        
        if n_epi % print_interval == 0 and n_epi != 0:
            print("timeLapse : ", timeLapse)
            print("# of episode : {}, avg score : {}".format(n_epi, score/print_interval))
            score = 0.0
            
            if timeLapse > goal*print_interval:
                print(__name__, "goal reached at episode : ", n_epi)
                break
            timeLapse = 0
            
    env.close()

# ================ TD Actor-Critic ================ #

class ActorCritic(nn.Module):
    def __init__(self):
        super(ActorCritic, self).__init__()
        self.data = []
        
        self.fc1 = nn.Linear(4, 128)
        self.fc_pi = nn.Linear(128, 2)
        self.fc_v = nn.Linear(128, 1)
        self.optimizer = optim.Adam(self.parameters(), lr=TDAC_learning_rate)
        
    def pi(self, x, softmax_dim = 0):
        x = F.relu(self.fc1(x))
        x = self.fc_pi(x)
        prob = F.softmax(x, dim = softmax_dim)
        return prob
    
    def v(self, x):
        x = F.relu(self.fc1(x))
        v = self.fc_v(x)
        return v
    
    def put_data(self, transition):
        self.data.append(transition)
    
    def make_data(self):
        s_lst, a_lst, r_lst, s_prime_lst, done_lst = [], [], [], [], []
        
        for transition in self.data:
            s, a, r, s_prime, done = transition
            s_lst.append(s)
            a_lst.append([a])
            r_lst.append([r/100.0])
            s_prime_lst.append(s_prime)
            done_mask = 0.0 if done else 1.0
            done_lst.append([done_mask])

        self.data = []
            
        return torch.tensor(np.array(s_lst), dtype=torch.float), torch.tensor(np.array(a_lst)), \
            torch.tensor(np.array(r_lst), dtype=torch.float), torch.tensor(np.array(s_prime_lst), dtype=torch.float), \
            torch.tensor(np.array(done_lst), dtype=torch.float)
    
    def train_net(self):
        s, a, r, s_prime, done = self.make_data()
        td_target = r + gamma * self.v(s_prime) * done
        delta = td_target - self.v(s)
        
        pi = self.pi(s, softmax_dim=1)
        pi_a = pi.gather(1, a)
        loss = -torch.log(pi_a) * delta.detach() + F.smooth_l1_loss(self.v(s), td_target.detach())
        
        self.optimizer.zero_grad()
        loss.mean().backward()
        self.optimizer.step()
        
def DTAC():
    env = gym.make('CartPole-v1')
    model = ActorCritic()
    
    print_interval = 20
    score = 0.0
    
    timeLapse = 0
    
    for n_epi in range(10000):
        done = False
        s, _ = env.reset()
        
        startTime = time.time()
        
        while not done:
            for i in range(n_rollout):
                prob = model.pi(torch.from_numpy(s).float())
                m = Categorical(prob)
                a = m.sample().item()
                s_prime, r, done, _, info = env.step(a)
                model.put_data((s, a, r, s_prime, done))
                
                s = s_prime
                score += r
                
                if done or time.time() > startTime + scoring_limitTimeout:
                    break
    
            model.train_net()
     
        print("time : ", time.time() - startTime)
        timeLapse += time.time() - startTime

        if n_epi % print_interval == 0 and n_epi != 0:
            print("timeLapse : ", timeLapse)
            print("# of episode : {}, avg score : {}".format(n_epi, score/print_interval))
            score = 0.0
            
            if timeLapse > goal*print_interval:
                print(__name__, "goal reached at episode : ", n_epi)
                break
            timeLapse = 0
            
    env.close()        

# ================ main ================ #

if __name__ == '__main__':
    DTAC()
    REINFORCE()
    DQNtest()
    NNtest()