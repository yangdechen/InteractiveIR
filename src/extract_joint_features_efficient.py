# File name: extract_joint_features_efficient.py
# Author: Yang-de Chen
# Date created: 12/22/2016
# Date modified: 12/22/2016
# python version: 3.5+
# Description:
#   Extract features from the graph of docuemnts and keywords
'''extract_joint_features_efficient.py

Usage:
    extract_joint_features_efficient.py <keyword-dir> <feat-type> <output>
    extract_joint_features_efficient.py -h
Options:
    -h --help       : show help messages
'''
from docopt import docopt
from collections import defaultdict
from util import read_keyword_dir
from util import alias_setup
from util import alias_draw
from util import normalize_to_prob
from tqdm import tqdm
import random

class FeatGraph:
    '''Perform node2vec with random walk + skip-gram'''

    def __init__(self, graph, node2id, rev_node2id, dim=64, p=1, q=1,
                 num_walks=5, walk_len=20):
        self.graph = graph
        self.node2id = node2id
        self.rev_node2id = rev_node2id
        self.dim = dim
        self.p = p
        self.q = q
        self.num_walks = num_walks
        self.walk_len = walk_len
        self.sample_node_graph = {}
        self.sample_edge_graph = {}
        self.__preprocess_transition_probs()

    def __preprocess_transition_probs(self):
        '''
        Preprocessing of transition probabilities for guilding the random walks
        '''
        print('=== preprocessing node start ===')
        for node in self.graph:
            edge_prob = normalize_to_prob(self.graph[node]['weight'])
            J, q = alias_setup(edge_prob)
            if node not in self.sample_node_graph:
                self.sample_node_graph[node] = {}
            self.sample_node_graph[node]['alias_table'] = J
            self.sample_node_graph[node]['alias_prob'] = q
        print('=== preprocessing node end ===')
        print('=== preprocessing edge start ===')
        for node in tqdm(self.graph):
            for nbr in self.graph[node]['adjacent']:
                J, q = self.__get_alias_edge(node, nbr)
                if (node, nbr) not in self.sample_edge_graph:
                    self.sample_edge_graph[(node, nbr)] = {}
                self.sample_edge_graph[(node, nbr)]['alias_table'] = J
                self.sample_edge_graph[(node, nbr)]['alias_prob'] = q
        print('=== preprocessing edge end ===')

    def __get_alias_edge(self, src, dst):
        weights = []
        for dst_nbr, dst_nbr_weight in zip(self.graph[dst]['adjacent'],
                                           self.graph[dst]['weight']):
            if dst_nbr == src:
                weights.append(dst_nbr_weight / self.p)
            elif src in self.graph[dst_nbr]['adj_dict']:
                weights.append(dst_nbr_weight)
            else:
                weights.append(dst_nbr_weight / self.q)
        return alias_setup(normalize_to_prob(weights))

    def run(self, n_iter=10):
        for _ in range(n_iter):
            pass
        walks = self.__random_walks()
        return walks

    def run_and_write(self, output_file, n_iter=10):
        for _ in range(n_iter):
            pass

        with open(output_file, 'w') as outfile:
            nodes = list(self.graph.keys())
            for walk_iter in range(self.num_walks):
                random.shuffle(nodes)
                for node in nodes:
                    walk = [self.rev_node2id[x] for x in \
                            self.__random_walk_from_node(node)]
                    outfile.write(' '.join(walk))
                    outfile.write('\n')

    def __random_walk_from_node(self, start_node):
        walk = [start_node]
        while len(walk) < self.walk_len:
            cur = walk[-1]
            cur_nbrs = self.graph[cur]['adjacent']
            cur_alias_table = self.sample_node_graph[cur]['alias_table']
            cur_alias_prob = self.sample_node_graph[cur]['alias_prob']
            if len(cur_nbrs) > 0:
                if len(walk) == 1:
                    walk.append(cur_nbrs[alias_draw(cur_alias_table,
                                                    cur_alias_prob)])
                else:
                    prev_node = walk[-2]
                    walk.append(
                        cur_nbrs[alias_draw(
                        self.sample_edge_graph[(prev_node,cur)]['alias_table'],
                        self.sample_edge_graph[(prev_node,cur)]['alias_prob'])]
                    )
            else:
                break
        return walk

    def __random_walks(self):
        walks = []
        nodes = list(self.graph.keys())
        for walk_iter in range(self.num_walks):
            random.shuffle(nodes)
            for node in nodes:
                walks.append(self.__random_walk_from_node(node))
        return walks

def build_graph(data_dict, thres=0.001):
    '''
    Construct a graph using data_dict, which has the following format:
    {item_i: [(item_j, score_j), (item_k, score_k)]}
    '''
    node2id = {}
    rev_node2id = {}
    graph = {}
    idx = 0
    print('=== build_graph start ===')
    for node, node_score_list in data_dict.items():
        for n, _ in node_score_list:
            if n not in node2id:
                node2id[n] = idx
                rev_node2id[idx] = n
                idx += 1
        for i in range(len(node_score_list)):
            for j in range(i+1, len(node_score_list)):
                node_1 = node2id[node_score_list[i][0]]
                node_2 = node2id[node_score_list[j][0]]
                if node_1 not in graph:
                    graph[node_1] = {'weight':[], 'adjacent': [],
                                     'adj_dict': set()}
                if node_2 not in graph:
                    graph[node_2] = {'weight':[], 'adjacent': [],
                                     'adj_dict': set()}
                graph[node_1]['adjacent'].append(node_2)
                graph[node_1]['weight'].append(
                    node_score_list[i][1] * node_score_list[j][1])
                graph[node_1]['adj_dict'].add(node_2)
                graph[node_2]['adjacent'].append(node_1)
                graph[node_2]['weight'].append(
                    node_score_list[i][1] * node_score_list[j][1])
                graph[node_2]['adj_dict'].add(node_1)
    print('=== build_graph end ===')

    return node2id, rev_node2id, graph

def main(docopt_args):
    '''Construct the graph and run node2vec to get node features'''
    keyword_dict = read_keyword_dir(docopt_args['<keyword-dir>'], thres=5)
    if docopt_args['<feat-type>'] == 'doc':
        rev_keyword_dict = defaultdict(list)
        for ind, (doc, keyword_list) in enumerate(keyword_dict.items()):
            for keyword, score in keyword_list:
                rev_keyword_dict[keyword].append((doc, score))
        node2id, rev_node2id, graph = build_graph(rev_keyword_dict)
    elif docopt_args['<feat-type>'] == 'keyword':
        node2id, rev_node2id, graph = build_graph(keyword_dict)

    print('setup up start')
    feat_graph = FeatGraph(graph, node2id, rev_node2id)
    print('setup up end')
    feat_graph.run_and_write(docopt_args['<output>'])

if __name__ == '__main__':
    main(docopt(__doc__))
