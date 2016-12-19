# File name: keyterm_generate.py
# Author: Yang-de Chen
# Date created: 12/14/2016
# Date modified: 12/19/2016
# python version: 3.5+
# Description:
#   Generate Keyword for each documents based on core-number and
#   TextRank algorithm.
'''Generate keyword for each documents

Usage:
    keyterm_generate.py <doc-dir> <stopword> <window-size> <outdir>
    keyterm_generate.py -h
Options:
    -h --help       : show help messages
'''
import os
import re
import sys
import pickle
import networkx as nx
from docopt import docopt
from math import log
from glob import glob
from operator import itemgetter
from util import walk_all_files
from util import read_stopwords

def main(docopt_args):
    '''
    Decide keyword via core-number * textrank, since both methods do not
    consider the highly connected phenomenon of stopwords, we should use a
    stopword list to achieve this goal.
    '''
    stopword = read_stopwords(docopt_args['<stopword>'])
    window_size = int(docopt_args['<window-size>'])

    for filename, filepath in walk_all_files(docopt_args['<doc-dir>']):
        text_graph = nx.Graph()
        with open(filepath) as ptv_file:
            for line in ptv_file:
                words = line.strip().split()
                for ind, node in enumerate(words):
                    # compute window boundaries
                    lower = ind - window_size \
                            if ind - window_size > 0 else 0
                    upper = ind + window_size \
                            if ind + window_size < len(words) else len(words)
                    for j in range(lower, upper):
                        if j != ind and node != words[j]:
                            if text_graph.has_edge(node, words[j]):
                                text_graph[node][words[j]]['weight'] += 1
                            else:
                                text_graph.add_edge(node, words[j], weight=1)
            # textrank method
            text_pagerank = nx.pagerank(text_graph)
            # compute core number
            text_core_rank = nx.core_number(text_graph)
        with open(filepath) as ptv_file, \
             open(os.path.join(docopt_args['<outdir>'], filename), 'w') as out:
            keywords = set()
            for line in ptv_file:
                words = line.strip().split()
                for node in words:
                    if node not in stopword and node in text_core_rank \
                        and len(node) > 1: # not count uni-char words
                        keywords.add((node, text_core_rank[node] * \
                                text_pagerank[node]))
            for k in sorted(keywords, key=itemgetter(1), reverse=True):
                out.write('{0} {1}\n'.format(k[0], k[1]))

if __name__ == '__main__':
    main(docopt(__doc__))
