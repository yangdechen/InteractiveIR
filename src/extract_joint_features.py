# File name: extract_joint_features.py
# Author: Yang-de Chen
# Date created: 12/20/2016
# Date modified: 12/20/2016
# python version: 3.5+
# Description:
#   Extract features from the graph of docuemnts and keywords
'''extract_joint_features.py

Usage:
    extract_joint_features.py <keyword-dir> <feat-type> <output>
    extract_joint_features.py -h
Options:
    -h --help       : show help messages
'''
import networkx as nx
from docopt import docopt
from collections import defaultdict
from util import read_keyword_dir

class FeatGraph:
    def __init__(self, graph, dim=64, p, q):
        self.graph = graph
        self.dim = dim
        self.p = p
        self.q = q

    def run(self, n_iter=10):
        for _ in range(n_iter):
            pass

def construct_doc_graph(keyword_dir):
    '''
    Construct document graph with sharing keywords as edges.
    doc_i and doc_j will have shared edges with weight equals
    to the summation over sharing keywords.
    (keyword weight in doc_i * keyword weight in doc_j)
    
    Returns:
      doc2id: map document name to id
      rev_doc2id: map id to document name
      doc_graph: doc-doc graph
    '''
    # This construction uses less memory
    keyword_dict = read_keyword_dir(keyword_dir)
    rev_keyword_dict = defaultdict(list)
    doc2id = {}
    rev_doc2id = {}
    doc_graph = nx.Graph()
    for ind, (doc, keyword_list) in enumerate(keyword_dict.items()):
        doc2id[doc] = ind
        rev_doc2id[ind] = doc
        for keyword, score in keyword_list:
            rev_keyword_dict[keyword].append((doc, score))
    for keyword, doc_list in rev_keyword_dict.items():
        for i in range(len(doc_list)):
            for j in range(i+1, len(doc_list)):
                node_1 = doc2id[doc_list[i][0]]
                node_2 = doc2id[doc_list[j][0]]
                if doc_graph.has_edge(node_1, node_2):
                    doc_graph[node_1][node_2]['weight'] += \
                        doc_list[i][1] * doc_list[j][1]
                else:
                    doc_graph.add_edge(node_1, node_2,
                        weight=doc_list[i][1] * doc_list[j][1])
    return doc2id, rev_doc2id, doc_graph

def construct_keyword_graph(keyword_dir):
    '''
    Construct keyword graph with sharing documents as edges.
    keyword_i and keyword_j will have shared edges with weight
    equals to the summation over sharing documents.
    (keyword_i weight in doc * keyword_j weight in doc)

    Returns:
      keyword2id: map keyword to id
      rev_keyword2id: map id to keyword
      keyword_graph: keyword-keyword graph
    '''
    # TODO: use too many memory, fix this.
    keyword_dict = read_keyword_dir(keyword_dir)
    keyword2id = {}
    rev_keyword2id = {}
    keyword_graph = nx.Graph()
    idx = 0;
    for doc, keyword_list in keyword_dict.items():
        for keyword, _ in keyword_list:
            if keyword not in keyword2id:
                keyword2id[keyword] = idx
                rev_keyword2id[idx] = keyword
                idx += 1
        for i in range(len(keyword_list)):
            for j in range(i+1, len(keyword_list)):
                node_1 = keyword2id[keyword_list[i][0]]
                node_2 = keyword2id[keyword_list[j][0]]
                if keyword_graph.has_edge(node_1, node_2):
                    keyword_graph[node_1][node_2]['weight'] += \
                        keyword_list[i][1] * keyword_list[j][1]
                else:
                    keyword_graph.add_edge(node_1, node_2,
                        weight=keyword_list[i][1] * keyword_list[j][1])
    return keyword2id, rev_keyword2id, keyword_graph

def main(docopt_args):
    '''Construct the graph and run node2vec to get node features'''
    if docopt_args['<feat-type>'] == 'doc':
        node2id, rev_node2id, graph = \
            construct_doc_graph(docopt_args['<keyword-dir>'])
    elif docopt_args['<feat-type>'] == 'keyword':
        node2id, rev_node2id, graph = \
            construct_keyword_graph(docopt_args['<keyword-dir>'])
    
    feat_graph = FeatGraph(graph)
    feat_graph.run()
    #with open(docopt_args['<output>'], 'w') as outfile:
    #    pass

if __name__ == '__main__':
    main(docopt(__doc__))
