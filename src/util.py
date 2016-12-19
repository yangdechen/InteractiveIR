# File name: util.py
# Author: Yang-de Chen
# Date created: 12/14/2016
# Date modified: 12/18/2016
# python version: 3.5+
# Description:
#   Utility function for convience.
import os
import pickle

def walk_all_files(dirname):
    '''Return an generator for all files in the "dirname"'''
    root, _, filenames = next(os.walk(dirname))
    for filename in filenames:
        yield (filename, os.path.join(root, filename))

def read_queries(filename):
    '''Read queries for experiments

    Args:
      filename: file name for query list, e.g. PTV.query
    Returns:
      query_list: list of queries, and each query is also a list
    '''
    query_list = []
    with open(filename) as f:
        for line in f:
            query_list.append(line.strip().split())
    return query_list

def read_answers(filename):
    '''Read answers for experiments

    Args:
      filename: file name for query answers, e.g. PTV.ans
    Returns:
      ans_dict: a dictionary that contains key-value pair
        (query, ans_list)
    '''
    ans_dict = {}
    with open(filename) as f:
        for line in f:
            query, ans_list = line.strip().split(None, 1)
            ans_dict[query] = set(ans_list.split())
    return ans_dict

def pickle_load(filename):
    '''To save typing'''
    with open(filename, 'rb') as f:
        return pickle.load(f)

def read_keyword_dir(dirname):
    '''Load keywords for each document'''
    keyword_dict = {}
    for filename, filepath in walk_all_files(dirname):
        with open(filepath) as keyfile:
            keyword_dict[filename] = []
            for line in keyfile:
                keyword, score = line.strip().split()
                keyword_dict[filename].append((keyword, float(score)))
    return keyword_dict

def read_stopwords(filename):
    '''Read stopwords from "filename", each line contains one stopword'''
    stopwords = set()
    with open(filename) as infile:
        for w in infile:
            stopwords.add(w.strip())
    return stopwords
