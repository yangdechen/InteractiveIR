# File name: agent.py
# Author: Yang-de Chen
# Date created: 12/11/2016
# Date modified: 12/18/2016
# python version: 3.5+
# Description:
#   User class should obtain the available actions from environemt, and
#   use different strategy to map state to action.
'''Agent class'''
from collections import deque
from strategy import Strategy
from environment import IIREnvironment
from tqdm import tqdm

class Agent:
    def __init__(self, env, history_len=5, train_pool_size=64,
            allowed_feedback_pos=5, feedback_weight=1, like_weight=1):
        '''Initialize necessary setup according to environment.
        Args:
          env: specify the environment
          history_len(default=5): how many steps you want your state represent
          train_pool_size(default=512): experience replay pool
          allowed_feedback_pos(default=5): If user feedback position is
            greater than this value, agent would get negative reward.
          feedback_weight(default=1): Weight the feedback position.
          like_weight(default=1): Weight the final like signal.
        '''
        self.env = env
        self.history = deque(maxlen=history_len)
        self.train_pool_size = train_pool_size
        self.training_pool = deque(maxlen=train_pool_size)
        self.rev_action_dict = self.env.get_actions()   # index to actions
        self.action_dict = { action: ind \
            for ind, action in enumerate(self.rev_action_dict) }
        self.action_num = len(self.action_dict)
        self.state_dim = 7
        self.strategy = Strategy(self.action_num, self.state_dim)
        self.allowed_feedback_pos = allowed_feedback_pos
        self.feedback_weight = feedback_weight
        self.like_weight = like_weight

    def play(self, n_episodes=10, isTraining=False):
        '''
        This method defines the interaction processes. And it is the
        starting point of the interaction.
        '''
        total_complete = 0
        total_queries = 0
        total_angry_percent = 0.0
        num_total_completed = 0
        data_collected_counter = 0
        total_rewards = 0.0
        for idx in tqdm(range(n_episodes)):
            observ, user = self.env.new_scenario()
            # prev-action, reward, observation
            self.history.append((None, 0, observ))
            # initial state
            state = self.__observation_to_state()
            current_reward = 0
            # TODO: Make this parallel.
            while True:     # In this loop, there's only one user.
                # Pick an action using current strategy.
                # During training, it will adopt epsilon-greedy and will
                # sometimes choose a random action to explore.
                # When testing, it will just take the optimal action.
                if isTraining:
                    action_id = self.strategy.step(state)
                else:
                    action_id = self.strategy.step(state, eps=0)
                action = self.rev_action_dict[action_id]
                # In current setup, observation is the ranking list.
                observation, like, terminal, feedback_pos = \
                                                        self.env.act(action)
                # If observation is None, either the user is satisfied
                # and continues on the next query (like=1) or just quit when
                # the feedback times exceeds his/her patience. (like=-1)
                if observation is not None:
                    # User react to the system action.
                    self.history.append((action, self.feedback_weight * (
                        self.allowed_feedback_pos - feedback_pos),
                        observation))
                    n_state = self.__observation_to_state()
                    self.training_pool.append((state, action_id, n_state,
                        self.feedback_weight * (
                        self.allowed_feedback_pos - feedback_pos)))
                    data_collected_counter += 1
                    state = n_state
                    # Besides the final "like" from the user, the system also
                    # want to rank relevant document or keyword higher.
                    # Thus the reward should be inversely proportional to
                    # the feedback position. 
                    current_reward += self.feedback_weight * (
                            self.allowed_feedback_pos - feedback_pos)
                else:
                    # User does not feedback.
                    self.training_pool.append((state, action_id, None,
                        self.like_weight * like))
                    data_collected_counter += 1
                    current_reward += self.like_weight * like
                    if terminal:
                        # User finish all his/her queries or quit with anger.
                        break
                    else:
                        # User is satisfied with the previous result and
                        # continues to use the system.
                        observ = self.env.next_query()
                        self.history.append((None, 0, observ))
                        state = self.__observation_to_state()
            if isTraining and data_collected_counter >= self.train_pool_size:
                self.strategy.update(self.training_pool)
                data_collected_counter = 0

            completed, num_queries, angry_percent = self.env.curr_user.stats()
            total_complete += completed
            total_queries += num_queries
            total_angry_percent += angry_percent
            total_rewards += current_reward
            if completed == num_queries:
                num_total_completed += 1
        # Show all the statistics
        print('======== Final Statistics =======')
        print('Avg. reward: {0:.2f}'.format(total_rewards / n_episodes))
        print('Avg. completed: {0:.2f}%'.format(
                100 * total_complete / total_queries))
        print('Avg. angry: {0:.2f}%'.format(
                100 * total_angry_percent / n_episodes))
        print('Number of total completed: ', num_total_completed)
        print('Number of total completed: {0:.2f}%'.format(
                num_total_completed / n_episodes))
        print('=================================')

    def __observation_to_state(self):
        '''Compute the state representation from the current history.
        '''
        # TODO: This is the MOST IMPORTANT part in this research.
        #   We need to compare tons of representation to confirm
        #   that joint represention of document and keyword could
        #   boost the performance and get more reasonable state
        #   representation to fulfill the Markov property during
        #   reinforcement learning.
        num_result = 5
        action, reward, observ = self.history[-1]
        feat = [0 for _ in range(self.action_num + num_result)]
        if action:
            feat[self.action_dict[action]] = 1
        for ind, (_, score) in enumerate(observ[:num_result]):
            feat[self.action_num + ind] = score
        return feat
