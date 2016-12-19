# File name: strategy.py
# Author: Yang-de Chen
# Date created: 12/12/2016
# Date modified: 12/18/2016
# python version: 3.5+
# Description:
#   Strategy implements different model to approximate Q-function, that is,
#   it implements a function that maps state-action pair to the estimate
#   expected return value.
'''strategy model'''
from random import randrange
from random import uniform
import numpy as np
# TODO: Finish the reinforcement learning
class Strategy:
    def __init__(self, num_actions, state_dim):
        self.num_actions = num_actions
        self.state_dim = state_dim
        # add one for bias
        self.w = np.random.rand(self.num_actions, self.state_dim + 1)

    def step(self, state, eps=0.01):
        if uniform(0, 1) < eps:
            return self.__random_action()
        else:
            return self.__optimal_action(state)

    def __random_action(self):
        return randrange(0, self.num_actions)

    def __optimal_action(self, state):
        action_value = [self.__Q_value(np.array(state + [1]),
            action) for action in range(self.num_actions)]
        return action_value.index(max(action_value))
    def __optimal_Q_value(self, state):
        return max([self.__Q_value(np.array(state + [1]),
            action) for action in range(self.num_actions)])

    def __Q_value(self, np_state, action):
        return np.dot(self.w[action], np_state)

    def update(self, train_data):
        '''Training. This method would change the paramenters'''
        X = [[] for _ in range(self.num_actions)]
        y = [[] for _ in range(self.num_actions)]
        for state, action, n_state, reward in train_data:
            # add bias
            X[action].append(state + [1])
            if n_state is None:
                # final state
                y[action].append(reward)
            else:
                # intermediate state
                y[action].append(reward + self.__optimal_Q_value(n_state))
        for action in range(self.num_actions):
            if len(X[action]) > 0:
                np_x = np.array(X[action])
                np_y = np.array(y[action])
                a = np.linalg.pinv(np.dot(np_x.T, np_x))
                b = np.dot(np_x.T, np_y)
                self.w[action] = np.dot(a, b)

