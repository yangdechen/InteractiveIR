# File name: user.py
# Author: Yang-de Chen
# Date created: 12/11/2016
# Date modified: 12/18/2016
# python version: 3.5+
# Description:
#   User specifies the simulation behavior, and decide the difficulties of
#   the task.
'''User class'''

POS_FEEDBACK=1
NEG_FEEDBACK=-1
NO_COMMENT=0

class User:
    sim_keyword = {}
    def __init__(self, query_list, ans_dict,
                 sim_keyword_file,
                 patience=5, ap_threshold=0.8):
        self.query_list = query_list
        self.curr_query_index = 0
        self.curr_query = self.query_list[self.curr_query_index]
        self.patience = patience
        self.ap_threshold = ap_threshold
        self.angry = 0
        self.ans_dict = ans_dict
        self.completed_queries = 0
        # TODO: remove this hard-code path
        if not User.sim_keyword:
            with open(sim_keyword_file) as f:
                for line in f:
                    query, *sim_key = line.strip().split()
                    User.sim_keyword[query] = set(sim_key)

    def __str__(self):
        info = 'query list: {0}\n'.format(str(self.query_list))
        info += 'current query: {0}\n'.format(str(self.curr_query))
        info += 'patience: {0}\n'.format(self.patience)
        info += 'ap threshold: {0}\n'.format(self.ap_threshold)
        info += 'angry: {0}'.format(self.angry)
        return info

    def eval_result(self, q, ranking_list):
        '''
        Simulated user evaluate the returned ranking list
        Args:
          q: the query this user use
          ranking_list: the ranking list that retrieval system returned
        Returns:
          AP: average precision for the query
        '''
        AP = 0.0
        num_ret = 0
        query = ''.join(q)
        for i, (d, score) in enumerate(ranking_list):
            if d in self.ans_dict[query]:
                num_ret += 1
                AP += num_ret / (i+1) / len(self.ans_dict[query])
        return AP
    def next_query(self):
        self.curr_query_index += 1
        self.curr_query = self.query_list[self.curr_query_index]

    def react(self, ranking_list, action, action_input):
        '''
        This function would increase user's anger. The less feedback,
        the better.
        '''
        user_feedback = None
        like = NO_COMMENT
        is_terminal = False
        ap = self.eval_result(self.curr_query, ranking_list)
        if ap >= self.ap_threshold:
            like = POS_FEEDBACK
            self.completed_queries += 1
            if self.curr_query_index + 1 >= len(self.query_list):
                is_terminal = True
        else:
            self.angry += 1
            if self.angry > self.patience:
                like = NEG_FEEDBACK
                is_terminal = True

        if not is_terminal and like != POS_FEEDBACK:
            if action == 'return_by_doc':
                user_feedback = self.__feedback_doc(action_input)
            elif action == 'return_by_keyterm':
                user_feedback = self.__feedback_keyword(action_input)
            if user_feedback is None:
                if self.curr_query_index + 1 >= len(self.query_list):
                    is_terminal = True

        return (user_feedback, like, is_terminal)

    def __feedback_doc(self, ranking_list):
        '''feedback document position '''
        for ind, (doc, score) in enumerate(ranking_list):
            if doc in self.ans_dict[''.join(self.curr_query)]:
                return ind
        return None

    def __feedback_keyword(self, keyword_list):
        '''feedback keyword position'''
        for ind, keyword in enumerate(keyword_list):
            if keyword in User.sim_keyword[''.join(self.curr_query)]:
                return ind
        return None
    def stats(self):
        '''This method is for performance measure.'''
        return (self.completed_queries / len(self.query_list),
                self.angry / self.patience)

