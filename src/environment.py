# File name: environment.py
# Author: Yang-de Chen
# Date created: 12/11/2016
# Date modified: 12/18/2016
# python version: 3.5+
# Description:
#   Environment class include
#       1. User class
#       2. RetrievalSystem class
#   Since we can not change them directly, they are part of the environment.
'''Environment class'''
import random
from operator import itemgetter
from math import ceil
from util import read_queries
from util import read_answers
from retrieval import RetrievalSystem
from user import User

class IIREnvironment:
    '''This is class is a composition of User and RetrievalSystem'''
    def __init__(self, query_file, ans_file, index_file, doclen_file,
                 bglm_file, keyword_dirname, doc_dir, sim_keyword_file,
                 max_queries=5, patience_mean=5, patience_std=2,
                 patience_min=1, ap_thres_mean=0.5, ap_thres_std=0.1,
                 ap_thres_min=0.1):
        self.query_list = read_queries(query_file)
        self.ans_dict = read_answers(ans_file)
        self.retrieval_system = RetrievalSystem(
                index_file, doclen_file, bglm_file, keyword_dirname, doc_dir)
        self.sim_keyword_file = sim_keyword_file
        self.max_queries = max_queries
        self.patience_mean = patience_mean
        self.patience_std = patience_std
        self.patience_min = patience_min
        self.ap_thres_mean = ap_thres_mean
        self.ap_thres_std = ap_thres_std
        self.ap_thres_min = ap_thres_min

        self.curr_user = None
        self.observation = None

    def act(self, action):
        '''Agent take actions through this method
        '''
        feedback_input_to_user = self.retrieval_system.request_feedback(action)
        user_feedback, like, is_terminal = self.curr_user.react(
                                            self.retrieval_system.ranking_list,
                                            action, feedback_input_to_user)
        self.observation = None
        if user_feedback is not None:
            self.observation = self.retrieval_system.feedback(action,
                                        feedback_input_to_user[user_feedback])
        return (self.observation, like, is_terminal, user_feedback)

    def __rand_patience(self):
        '''Generate user patience with Gaussian distribution'''
        # TODO: Other distribution is also possible.
        patience = ceil(random.gauss(self.patience_mean, self.patience_std)) 
        return patience if patience >= self.patience_min else self.patience_min

    def __rand_query_num(self):
        '''Generate query number using uniform distribution'''
        # TODO: Other distribution is also possible.
        return random.randint(1, self.max_queries)

    def __rand_ap_threshold(self):
        '''Generate ap threshold with Gaussian distribution'''
        # TODO: Other distribution is also possible.
        ap_thres = random.gauss(self.ap_thres_mean, self.ap_thres_std)
        return ap_thres if ap_thres > self.ap_thres_min else self.ap_thres_min

    def __rand_user(self):
        '''
        Create a user with random query list, patience and ap threshold.
        '''
        # TODO: Even with the same query, each user can have different answers.
        random_query = random.sample(self.query_list, self.__rand_query_num())
        user_ans = {''.join(q):self.ans_dict[''.join(q)] for q in random_query}
        return User(random_query, user_ans, self.sim_keyword_file,
                    self.__rand_patience(), self.__rand_ap_threshold())

    def new_scenario(self):
        '''New user comes in, which indicates a new episode.

        Returns:
          observation: ranking list based on current user query
          curr_user: random user
        '''
        # TODO: Maybe we can specify user type.
        self.curr_user = self.__rand_user()
        self.observation = \
            self.retrieval_system.query(self.curr_user.curr_query)
        return (self.observation, self.curr_user)

    def next_query(self):
        '''
        When the user is satisfied with previous query, and want to
        continue on the next query.

        Returns:
          observation: new ranking list
        '''
        self.curr_user.next_query()
        self.observation = \
            self.retrieval_system.query(self.curr_user.curr_query)
        return self.observation

    def get_actions(self):
        '''To let agent know available actions'''
        return self.retrieval_system.get_actions()
