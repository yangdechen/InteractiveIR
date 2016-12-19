# File name: retrieval.py
# Author: Yang-de Chen
# Date created: 12/11/2016
# Date modified: 12/18/2016
# python version: 3.5+
# Description:
#   Retrieval system implements the interface to retrieve documents and
#   the desired framework to add different interactive actions
#   NOTICE: if you add additional interface to support additional action,
#   you should implement the corresponding feedback interface to User class to
#   support the simulation.
'''Retrieval system'''
import os
import pickle
from math import log2
from copy import deepcopy
from operator import itemgetter
from collections import defaultdict
from util import *

class RetrievalSystem:
    '''
    This class implements language model retrieval with Dirichlet prior
    '''
    def __init__(self,
                 index_file,    # inverted index
                 doclen_file,   # to enable document length normalization
                 bglm_file,     # statistic to enable background smoothing
                 keyword_dirname, # to support "feedback by keyword" action
                 doc_dir,        # to support "feedback by document" action
                 mu=1000,       # Dirichlet prior parameter
                 char_weight=1.0,   # character-based retrieval weight
                 bichar_weight=1.0): # bi-character-based retrieval weight
        # read all relevant files
        # TODO: Although pickle is convienent, it is not space efficient.
        #   What's worse, you should read the source code to figure out the
        #   representation of the object.
        #   Change these to some other serial object.
        self.index_dict = pickle_load(index_file)
        self.doclen_dict = pickle_load(doclen_file)
        self.bglm_dict = pickle_load(bglm_file)
        self.keyword_dict = read_keyword_dir(keyword_dirname)
        # initialize parameters
        self.mu = mu
        self.char_weight = char_weight;
        self.bichar_weight = bichar_weight
        
        # record current ranking list
        ## this should be changed in the need of parallel processing
        self.ranking_list = None
        self.score_dict = None
        self.queries = None
        # after we identify the desired document ID, we need to retrieve the
        # corresponding documents from the disk
        # but to accelerate the whole process, we load all data in 
        self.doc_dict = {}
        for filename, filepath in walk_all_files(doc_dir):
            self.doc_dict[filename] = []
            with open(filepath) as docfile:
                for line in docfile:
                    self.doc_dict[filename].extend(line.strip().split())
        # Avoid redundant feedback, and accumulate information.
        # If add another action, this should also fix.
        self.past_feedback_keyword = set()
        self.past_feedback_doc = set()

    def query(self, q, retrieval_method='lang'):
        '''Return retrieval results
        
        Now, it seems redundant, but it enables us to change the underlying
        retrieval mechanism.
        Every time you use this function, you will change self.queries
        and self.ranking_list.

        Args:
          q: input query, which is a list
          retrieval_method(default=lang): retrieval model
        Returns:
          ranking_list: retrieval result
        '''
        self.past_feedback_doc = set()
        self.past_feedback_keyword = set()
        self.queries = q
        if retrieval_method == 'lang':
            score_dict = self.__lang_score(q)
        self.score_dict = score_dict
        self.ranking_list = sorted(score_dict.items(), key=itemgetter(1),
                                   reverse=True)
        return self.ranking_list

    # the followings are support feedback actions
    def get_actions(self):
        '''Return all available actions'''
        return ['return_by_doc', 'return_by_keyterm']

    def lang_score_feedback(self, q, feedback_doc, weight=0.05):
        score_dict = self.__lang_score(q)
        feedback_dict = self.__lang_score(feedback_doc)
        new_score_dict = self.__merge_score(score_dict, feedback_dict, weight)
        self.score_dict = new_score_dict
        self.ranking_list = sorted(new_score_dict.items(), key=itemgetter(1),
                                   reverse=True)
        return self.ranking_list

    def request_feedback(self, action):
        '''Use the necessary input according to the action
        '''
        # TODO: Add more actions here.
        # TODO: Customize to the screen size.
        if action == 'return_by_doc':
            # Give users the ranking list.
            return self.__return_by_doc_request()
        elif action == 'return_by_keyterm':
            # Give users the keyword list.
            return self.__return_by_keyterm_request()

    def feedback(self, action, feedback_input):
        '''Now, I only utilize the positive feedback.'''
        if action == 'return_by_doc':
            self.past_feedback_doc.add(feedback_input[0])
            return self.lang_score_feedback(self.queries,
                                [''.join(self.doc_dict[feedback_input[0]])])
        elif action == 'return_by_keyterm':
            self.past_feedback_keyword.add(feedback_input)
            return self.lang_score_feedback(self.queries, [feedback_input])

    def __return_by_doc_request(self):
        '''Return whole ranking list'''
        feedback_doc_dict = deepcopy(self.score_dict)
        for doc_id in self.past_feedback_doc:
            del feedback_doc_dict[doc_id]
        return sorted(feedback_doc_dict.items(), key=itemgetter(1),
                      reverse=True)

    def __return_by_keyterm_request(self, num_docs=30, num_keys=50):
        '''
        choose those keywords that have high entropy in top ranking list
        '''
        # Top-"num_docs" document set
        rankset = set(x[0] for x in self.ranking_list[:num_docs])
        # doc_num may be less than num_docs
        doc_num = len(rankset)
        counter = defaultdict(int)
        for doc in rankset:
            # Count each word in each document only once.
            doc_word = set(self.doc_dict[doc])
            for word in doc_word:
                counter[word] += 1
        # Load all the keywords contained in the top documents.
        keywords = []
        for doc in rankset:
            keywords.extend(self.keyword_dict[doc])
        # keyword ranking according their textrank * main-core score
        keyrank = [x[0] for x in sorted(keywords, key=itemgetter(1),
                                        reverse=True)]
        high_entropy_keyword = []
        # Remove keywords that are counted multiple times.
        keyword_set = set()
        for keyword in keyrank[:num_keys]:
            if len(high_entropy_keyword) > num_keys:
                break
            if keyword in counter and keyword not in keyword_set and \
                        keyword not in self.past_feedback_keyword:
                keyword_set.add(keyword)
                high_entropy_keyword.append((keyword,
                    counter[keyword] / doc_num * log2 (
                    doc_num / counter[keyword])))
        sorted_high_entropy_key = [x[0] for x in sorted(
                high_entropy_keyword, key=itemgetter(1), reverse=True)]
        return sorted_high_entropy_key

    def __merge_score(self, dict1, dict2, weight=0.1):
        for k, v in dict2.items():
            dict1[k] += weight * v
        return dict1

    def __lang_score(self, q):
        '''
        Args:
          q: query, which is a word list
        Returns:
          score_dict: a dict with key-value pair: (doc-id, score)
        '''
        score_dict = defaultdict(float)
        mu = self.mu
        for text in q: # loop over all words
            for ch in text: # loop over all characters
                if ch in self.index_dict:
                    for doc, tf in self.index_dict[ch]['docs'].items():
                        score_dict[doc] += self.char_weight * log2(
                                (mu + tf / self.bglm_dict[ch]) / \
                                (mu + self.doclen_dict[doc]))
            for i in range(1, len(text)): # loop over all bi-characters
                bichar = text[i-1] + text[i]
                if bichar in self.index_dict:
                    for doc, tf in self.index_dict[bichar]['docs'].items():
                        score_dict[doc] += self.bichar_weight * log2(
                                (mu + tf / self.bglm_dict[bichar]) / \
                                (mu + self.doclen_dict[doc]))
        return score_dict
