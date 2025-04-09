
#
import time
import glob
import os

# for DQN testing
# import gymnasium as gym
import gym
import collections
import random

#
import gym_chess
import chess
import bit_board_chess

#
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from torch.distributions import Categorical

import numpy as np
import matplotlib.pyplot as plt

# local module
from chess_bitmap_module import *

if torch.cuda.is_available():
    device = torch.device("cuda")
    device = torch.device("cpu")
else:
    raise Exception("CUDA is not available")

# Hyperparameters
IS_LOADING = True
SKIPDRAWGAME = True
SKIPTRAINING = True
LOAD_PATH = os.path.join(
    f'd:\RFData', f'model20241025004508_0.135')
SAVE_PATH = os.path.join(
    f'd:\RFData', f'model{time.strftime('%Y%m%d%H%M%S')}')
SELFTRAINIG_DATA_NAMES = f'd:\RFData\*.npy'

TDAC_learning_rate = 0.00005
gamma = 0.98

# troubleshooting
np.bool8 = np.bool

# ================ ChessRL ================ #


class ChessActorCritic(nn.Module):
    def __init__(self):
        super(ChessActorCritic, self).__init__()

        # batch Database
        self.data = [[] for _ in range(64)]
        self.nonDrawData = []

        # waights settings
        self.fc1 = nn.Linear(512, 1024)
        self.fc2 = nn.Linear(1024, 2048)
        self.fc_pi = nn.Linear(2048, 4288)
        self.fc_v = nn.Linear(2048, 1)

        # optimizer
        self.optimizer = optim.Adam(self.parameters(), lr=TDAC_learning_rate)

    def setOptimizerLr(self, learning_rate):
        self.optimizer = optim.Adam(self.parameters(), lr=learning_rate)

    def pi(self, x, filter):
        x = F.elu(self.fc1(x))
        x = F.elu(self.fc2(x))
        x = F.elu(self.fc_pi(x))

        # filter illegal moves
        x *= filter.detach()

        return x

    def v(self, x):
        x = F.elu(self.fc1(x))
        x = F.elu(self.fc2(x))
        v = self.fc_v(x)

        return v

    def put_data(self, transition, index):
        self.data[index].append(transition)

    def save_nonDrawData(self, episode):
        '''
        stack non-draw data to nonDrawData list for collect training data
        :param episode: tuple of (s, a, r, s_prime, s_filter, done_mask)
        '''
        s, a, r, s_prime, s_filter, done_mask = episode

        episode = (
            s.cpu().numpy(),
            a.cpu().numpy(),
            r.cpu().numpy(),
            s_prime.cpu().numpy(),
            s_filter.cpu().numpy(),
            done_mask.cpu().numpy()
        )

        self.nonDrawData.append(episode)

    def make_data(self, index):
        s_lst, a_lst, r_lst, s_prime_lst, s_filter_lst, done_mask_lst = \
            [], [], [], [], [], []

        for transition in self.data[index]:
            # load the transition
            s, a, r, s_prime, s_filter, done = transition

            s_lst.append(s)
            s_filter_lst.append(s_filter)
            s_prime_lst.append(s_prime)

            a_lst.append([a.cpu()])
            r_lst.append([r])

            done_mask = 0.0 if done else 1.0
            done_mask_lst.append([done_mask])

        # reset
        self.data[index] = []

        return torch.stack(s_lst, 0).to(torch.float), \
            torch.tensor(np.array(a_lst)).to(device=device), \
            torch.Tensor(r_lst).to(device=device), \
            torch.stack(s_prime_lst, 0).to(torch.float), \
            torch.stack(s_filter_lst, 0).to(torch.float), \
            torch.Tensor(done_mask_lst).to(device=device)

    def train_net(self, index, reward, interval=0, score=0):
        # load training
        s, a, r, s_prime, s_filter, done_mask = self.make_data(index)

        # calculate reward
        processTurn = len(r)
        winningRateFactor = 1.0 - (score/(interval+1))
        adjusted_reward = (reward/np.sqrt(processTurn)) * \
            winningRateFactor*winningRateFactor

        r = torch.Tensor(
            np.flip((np.full(processTurn, 0.98) ** np.arange(processTurn)
                     ).astype(float).reshape([processTurn, 1]))
            * adjusted_reward).to(device=device)

        print(index, processTurn, winningRateFactor)

        if reward == 0.0 and SKIPDRAWGAME:
            return

        # if episode is not draw, save the data
        if reward != 0.0 and processTurn < 100:
            self.save_nonDrawData((s, a, r, s_prime, s_filter, done_mask))

        # calculate td_target and delta
        td_target = r + gamma * self.v(s_prime) * done_mask
        delta = td_target - self.v(s)

        # probability space of action
        pi = self.pi(s, s_filter)
        pi += (0.0001 * s_filter)
        pi = pi / pi.sum(1, keepdim=True)

        # get action probability
        pi_a = pi.gather(1, a)

        # loss function
        loss = -torch.log(pi_a) * delta.detach() + \
            F.smooth_l1_loss(
                self.v(s), td_target.detach())

        # update weights
        self.optimizer.zero_grad()
        loss.mean().backward()
        self.optimizer.step()

    def train_net_withData(self, Data, waightFactor):
        for episode in Data:
            s, a, r, s_prime, s_filter, done_mask = episode
            # preprocess data
            s = torch.from_numpy(s).to(device=device)
            a = torch.from_numpy(a).to(device=device)
            r = torch.from_numpy(r)
            s_prime = torch.from_numpy(s_prime).to(device=device)
            s_filter = torch.from_numpy(s_filter).to(device=device)
            done_mask = torch.from_numpy(done_mask).to(device=device)

            # calculate reward
            processTurn = len(r)
            print(processTurn)
            if processTurn > 100:
                continue

            reward = waightFactor if (r[-1] > 0) else -waightFactor
            adjusted_reward = (reward/np.sqrt(processTurn))

            r = torch.Tensor(
                np.flip((np.full(processTurn, 0.98) ** np.arange(processTurn)
                         ).astype(float).reshape([processTurn, 1]))
                * adjusted_reward).to(device=device)

            # calculate td_target and delta
            td_target = r + gamma * self.v(s_prime) * done_mask
            delta = td_target - self.v(s)

            # probability space of action
            pi = self.pi(s, s_filter)
            pi += (0.0001 * s_filter)
            pi = pi / pi.sum(1, keepdim=True)

            # get action probability
            pi_a = pi.gather(1, a)

            # loss function
            loss = -torch.log(pi_a) * delta.detach() + \
                F.smooth_l1_loss(
                    self.v(s), td_target.detach())

            # update weights
            self.optimizer.zero_grad()
            loss.mean().backward()
            self.optimizer.step()


def output(sideToMove: str, board: list[int]):
    model = ChessActorCritic()
    model.load_state_dict(torch.load(LOAD_PATH, weights_only=True))

    chess = bit_board_chess.Chess()
    chess._set(sideToMove, board)

    s = torch.Tensor(board2NNinput2(board))[0:4096].to(torch.float)
    filter = chess.getPossibleMoveBBs(1 if sideToMove == 'w' else 2)
    filter = torch.stack([torch.Tensor(item)
                          for item in filter], 0).to(torch.float).reshape(4288)

    prob = model.pi(s, filter).clamp(min=0)
    prob += (0.0001 * filter)
    prob = prob / prob.sum(0, keepdim=True)
    a = prob[0:4096].argmax()
    a_prob = prob[a]

    print(a)
    print(f'{a_prob:0.4f}')


def ChessDTAC(lr=TDAC_learning_rate):
    # set model and environment
    model = ChessActorCritic()
    model.setOptimizerLr(lr)
    num_env = 64
    Env = [gym.make('Chess-v0') for _ in range(num_env)]

    # load model
    if IS_LOADING:
        model.load_state_dict(torch.load(LOAD_PATH, weights_only=True))
        print(LOAD_PATH)

    # set save path
    savepathName = SAVE_PATH

    # set device
    model.to(device)

    # set parameter
    print_interval = 20

    # set variables
    score = 0.0
    timeLapse = 0
    benchMark = 0
    n_epi = 0
    processTurn = 0

    interval = 0
    save_interval = 0
    winning_rate = 0.0
    max_winning_rate = 0.0

    # set const variables
    none_list = [0.0 for _ in range(num_env)]
    none_blist = [False for _ in range(num_env)]
    init_s = [env.reset() for env in Env]

    # ======== training nonDraw data ======== #

    if SKIPTRAINING == False:
        trainging_data_fileNames = glob.glob(SELFTRAINIG_DATA_NAMES)
        waightFactor = 1/np.sqrt(len(trainging_data_fileNames))
        for fileName in trainging_data_fileNames:
            print(fileName)
            training_data = np.load(fileName, allow_pickle=True)
            model.train_net_withData(training_data, waightFactor)

    # ======== processing ======== #

    # s = env.reset()
    s = init_s
    s_prime = init_s

    # get state and filter
    s = [Fen2NNinput2(state.fen()) for state in s]
    s = torch.stack(s, 0).to(torch.float).to(device=device)

    while n_epi < 30:
        # set time
        startTime = time.time()

        # set variables and models
        done = [False for _ in range(num_env)]
        r = [0.0 for _ in range(num_env)]

        # set filter
        legalIndex = [torch.Tensor(
            [uci2actIndex(move) for move in para_env.legal_moves])
            .to(torch.int64).to(device=device)
            for para_env in Env]

        filter = torch.zeros(4288).to(torch.int64).to(device=device)
        filter = [filter.scatter(
            0, legalIndex[index], torch.ones(legalIndex[index].size(dim=0)).to(torch.int64).to(device=device))
            for index in range(num_env)]
        filter = torch.stack(filter, 0).to(torch.float).to(device=device)

        # training
        while r == none_list:
            benchMarkTime = time.time()

            # probability space of action and sample action
            prob = model.pi(s, filter).clamp(min=0)
            prob += (0.0001 * filter)
            prob.max
            prob = Categorical(prob)
            a = prob.sample()

            benchMark += (time.time() - benchMarkTime)

            # update environment and get next state
            for index in range(num_env):
                s_prime[index], r[index], done[index], _ \
                    = Env[index].step(NNoutput2uciMove(a[index]))

            # get s_prime
            s_prime = [Fen2NNinput2(state.fen()) for state in s_prime]
            s_prime = torch.stack(s_prime, 0).to(torch.float).to(device=device)

            # put data
            for index in range(num_env):
                model.put_data((s[index], a[index], r[index],
                               s_prime[index], filter[index], done[index]), index)

            # Update state
            s = s_prime
            s_prime = init_s

            # game is done, reset game state
            processTurn += 1
            if done != none_blist:
                break

            # ======== opponent state ======== #

            benchMarkTime = time.time()

            # opponent's turn : move randomization
            opponentMov = [random.choice(env.legal_moves)
                           for env in Env]

            benchMark += (time.time() - benchMarkTime)

            # update environment and get next state
            for index in range(num_env):
                s_prime[index], r[index], done[index], _ \
                    = Env[index].step(opponentMov[index])

            # get s_prime
            s_prime = [Fen2NNinput2(state.fen()) for state in s_prime]
            s_prime = torch.stack(s_prime, 0).to(torch.float).to(device=device)

            # Update state
            s = s_prime
            s_prime = init_s

            # game is done, reset game state
            processTurn += 1
            if done != none_blist:
                break

            # Update filter
            legalIndex = [torch.Tensor(
                [uci2actIndex(move)
                 for move in para_env.legal_moves]).to(torch.int64).to(device=device)
                for para_env in Env]

            filter = torch.zeros(4288).to(torch.int64).to(device=device)
            filter = [filter.scatter(
                0, legalIndex[index], torch.ones(legalIndex[index].size(dim=0)).to(torch.int64).to(device=device))
                for index in range(num_env)]
            filter = torch.stack(filter, 0).to(torch.float).to(device=device)

        # training terminated episode

        for index in range(num_env):
            if done[index]:
                # update
                n_epi += 1
                interval += 1
                save_interval += 1
                score += r[index]

                benchMarkTime = time.time()
                # train model
                model.train_net(index, r[index], interval, score)
                benchMark += (time.time() - benchMarkTime)

                # reset environment
                temp_s = Env[index].reset()
                s[index] = Fen2NNinput2(temp_s.fen())

        # print time and score
        print(f'time : {time.time() - startTime}, score : {score}')
        timeLapse += time.time() - startTime

        if interval > print_interval:
            # print time and score
            print(f'timeLapse : {timeLapse}')
            print(f'# of episode : {n_epi}, avg score : {
                  score/print_interval}')
            print(f'benchmark : {benchMark/timeLapse}, processTurn : {
                  processTurn}, timePerturn : {timeLapse/processTurn}')

            # update winning rate
            winning_rate = winning_rate * 0.9 + 0.1 * (score / interval)
            if max_winning_rate < score/print_interval:
                max_winning_rate = score/print_interval
                winratepathName = f'{savepathName}_winrate_{
                    max_winning_rate:.2f}.pth'
                # save peek winning model
                torch.save(model.state_dict(), winratepathName)

            # reset variables
            score = 0.0
            timeLapse = 0
            benchMark = 0
            processTurn = 0
            interval = interval % print_interval

            # save model
            torch.save(model.state_dict(), savepathName)
            model.load_state_dict(torch.load(
                savepathName, weights_only=True, map_location=torch.device('cpu')))
            print('save model')
            torch.save(model.state_dict(), savepathName)

        # save nonDrawData
        if save_interval > 1000:
            save_interval = save_interval % 1000
            np.save(f'{savepathName}_nonDrawData_{n_epi}.npy',
                    np.array(model.nonDrawData, dtype=object).astype(object, copy=False))
            model.nonDrawData = []

        # goal reached
        if score > 0.9 * print_interval:
            print(savepathName, "goal reached at episode : ", n_epi)
            torch.save(model.state_dict(), savepathName)
            break

    # save model
    torch.save(model.state_dict(), f'{savepathName}_{winning_rate:.3f}')
    # close environment
    for env in Env:
        env.close()


def findOptimalLRateOfChessDTAC(initialLRate, rangeMultiplier, numLRate):
    # set model and environment
    model = ChessActorCritic()
    num_env = 64
    Env = [gym.make('Chess-v0') for _ in range(num_env)]

    minLRate = initialLRate/rangeMultiplier
    maxLRate = initialLRate*rangeMultiplier

    winning_rates = [0.0 for _ in range(numLRate)]
    peek_winning_rates = [0.0 for _ in range(numLRate)]
    TDAC_learning_rates = np.arange(
        minLRate, maxLRate, (maxLRate-minLRate)/numLRate)

    for i, lr in enumerate(TDAC_learning_rates):

        # set optimizer
        model.setOptimizerLr(lr)

        # set save path
        savepathName = os.path.join(
            f'd:\RFData', f'model{time.strftime('%Y%m%d%H%M%S')}_lr{lr:.6f}')

        # set device
        model.to(device)

        # set parameter
        print_interval = 20

        # set variables
        score = 0.0
        timeLapse = 0
        benchMark = 0
        n_epi = 0
        processTurn = 0

        interval = 0
        save_interval = 0
        winning_rate = 0.0
        max_winning_rate = 0.0

        # set const variables
        none_list = [0.0 for _ in range(num_env)]
        none_blist = [False for _ in range(num_env)]
        init_s = [env.reset() for env in Env]

        # ======== training nonDraw data ======== #

        trainging_data_fileNames = glob.glob(f'd:\RFData\*.npy')
        waightFactor = 1/np.sqrt(len(trainging_data_fileNames))
        for fileName in trainging_data_fileNames:
            print(fileName)
            training_data = np.load(fileName, allow_pickle=True)
            model.train_net_withData(training_data, waightFactor)

        # ======== processing ======== #

        # s = env.reset()
        s = init_s
        s_prime = init_s

        # get state and filter
        s = [Fen2NNinput2(state.fen()) for state in s]
        s = torch.stack(s, 0).to(torch.float).to(device=device)

        while n_epi < 300:
            # set time
            startTime = time.time()

            # set variables and models
            done = [False for _ in range(num_env)]
            r = [0.0 for _ in range(num_env)]

            # set filter
            legalIndex = [torch.Tensor(
                [uci2actIndex(move) for move in para_env.legal_moves])
                .to(torch.int64).to(device=device)
                for para_env in Env]

            filter = torch.zeros(4288).to(torch.int64).to(device=device)
            filter = [filter.scatter(
                0, legalIndex[index], torch.ones(legalIndex[index].size(dim=0)).to(torch.int64).to(device=device))
                for index in range(num_env)]
            filter = torch.stack(filter, 0).to(torch.float).to(device=device)

            # training
            while r == none_list:
                benchMarkTime = time.time()

                # probability space of action and sample action
                prob = model.pi(s, filter).clamp(min=0)
                prob += (0.0001 * filter)
                prob = Categorical(prob)
                a = prob.sample()

                benchMark += (time.time() - benchMarkTime)

                # update environment and get next state
                for index in range(num_env):
                    s_prime[index], r[index], done[index], _ \
                        = Env[index].step(NNoutput2uciMove(a[index]))

                # get s_prime
                s_prime = [Fen2NNinput2(state.fen()) for state in s_prime]
                s_prime = torch.stack(s_prime, 0).to(
                    torch.float).to(device=device)

                # put data
                for index in range(num_env):
                    model.put_data((s[index], a[index], r[index],
                                    s_prime[index], filter[index], done[index]), index)

                # Update state
                s = s_prime
                s_prime = init_s

                # game is done, reset game state
                processTurn += 1
                if done != none_blist:
                    break

                # ======== opponent state ======== #

                benchMarkTime = time.time()

                # opponent's turn : move randomization
                opponentMov = [random.choice(env.legal_moves)
                               for env in Env]

                benchMark += (time.time() - benchMarkTime)

                # update environment and get next state
                for index in range(num_env):
                    s_prime[index], r[index], done[index], _ \
                        = Env[index].step(opponentMov[index])

                # get s_prime
                s_prime = [Fen2NNinput2(state.fen()) for state in s_prime]
                s_prime = torch.stack(s_prime, 0).to(
                    torch.float).to(device=device)

                # Update state
                s = s_prime
                s_prime = init_s

                # game is done, reset game state
                processTurn += 1
                if done != none_blist:
                    break

                # Update filter
                legalIndex = [torch.Tensor(
                    [uci2actIndex(move)
                     for move in para_env.legal_moves]).to(torch.int64).to(device=device)
                    for para_env in Env]

                filter = torch.zeros(4288).to(torch.int64).to(device=device)
                filter = [filter.scatter(
                    0, legalIndex[index], torch.ones(legalIndex[index].size(dim=0)).to(torch.int64).to(device=device))
                    for index in range(num_env)]
                filter = torch.stack(filter, 0).to(
                    torch.float).to(device=device)

            # training terminated episode

            for index in range(num_env):
                if done[index]:
                    # update
                    n_epi += 1
                    interval += 1
                    save_interval += 1
                    score += r[index]

                    benchMarkTime = time.time()
                    # train model
                    model.train_net(index, r[index], interval, score)
                    benchMark += (time.time() - benchMarkTime)

                    # reset environment
                    temp_s = Env[index].reset()
                    s[index] = Fen2NNinput2(temp_s.fen())

            # print time and score
            print(f'time : {time.time() - startTime}, score : {score}')
            timeLapse += time.time() - startTime

            if interval > print_interval:
                # print time and score
                print(f'timeLapse : {timeLapse}')
                print(f'# of episode : {n_epi}, avg score : {
                    score/print_interval}')
                print(f'benchmark : {benchMark/timeLapse}, processTurn : {
                    processTurn}, timePerturn : {timeLapse/processTurn}')

                # update winning rate
                winning_rate = winning_rate * 0.9 + 0.1 * (score / interval)
                if max_winning_rate < score/print_interval:
                    max_winning_rate = score/print_interval
                    winratepathName = f'{savepathName}_winrate_{
                        max_winning_rate:.2f}_epi{n_epi}.pth'
                    # save peek winning model
                    torch.save(model.state_dict(), winratepathName)

                # reset variables
                score = 0.0
                timeLapse = 0
                benchMark = 0
                processTurn = 0
                interval = interval % print_interval

            # save nonDrawData
            if save_interval > 1000:
                model.nonDrawData = []

            # goal reached
            if score > 0.9 * print_interval:
                print(savepathName, "goal reached at episode : ", n_epi)
                torch.save(model.state_dict(), savepathName,
                           map_location=torch.device('cpu'))
                winning_rates[i] = winning_rate
                peek_winning_rates[i] = max_winning_rate
                break

        # save model
        winning_rates[i] = winning_rate
        peek_winning_rates[i] = max_winning_rate
        # close environment
        for env in Env:
            env.close()

    max_winning_rate = max(peek_winning_rates)

    plt.plot(TDAC_learning_rates, winning_rates, label="winning rate")
    plt.plot(TDAC_learning_rates, peek_winning_rates,
             label="peek_winning_rates")
    plt.legend()
    plt.savefig(os.path.join(
        f'd:\RFData', f'{max_winning_rate}_{time.strftime('%Y%m%d%H%M%S')}.png'))

    return max_winning_rate


# ================ ChessRL end ================ #

# ================ main ================ #


if __name__ == '__main__':

    adjustLR = findOptimalLRateOfChessDTAC(TDAC_learning_rate, 4, 10)
    ChessDTAC(adjustLR)

    raise Exception
    NNtest()
    DQNtest()
    REINFORCE()
    DTAC()
