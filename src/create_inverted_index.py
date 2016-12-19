# File name: create_inverted_index.py
# Author: Yang-de Chen
# Date created: 12/14/2016
# Date modified: 12/18/2016
# python version: 3.5+
# Description:
#   Run interactive retrieval experiment.
"""create_inverted_index.py
    
Usage:
    create_inverted_index.py <corpus_dir> <inv_index_output>
    create_inverted_index.py -h
Options:
    -h --help       : show help message
"""
import sys
import pickle
from util import walk_all_files
from docopt import docopt

# index format: token: [total, docs: (file, tf), df]
index_dict = dict()

def add_token_index(token, filename):
    if token not in index_dict:
        index_dict[token] = {}
        index_dict[token]['total'] = 0
        index_dict[token]['docs'] = {}
        index_dict[token]['df'] = 0
    index_dict[token]['total'] += 1
    # store document term freq.
    index_dict[token]['docs'][filename] = \
        index_dict[token]['docs'].get(filename, 0) + 1
    index_dict[token]['df'] = len(index_dict[token]['docs'].keys())

def add_char_index(text, filename):
    for ch in text:
        add_token_index(ch, filename)

def add_bichar_index(text, filename):
    for i in range(1, len(text)):
        bichar = text[i-1] + text[i]
        add_token_index(bichar, filename)

def main(docopt_args):
    all_files = walk_all_files(docopt_args['<corpus_dir>'])
    for filename, filepath in all_files:
        with open(filepath) as f:
            for line in f:
                text = ''.join(line.strip().split())
                add_char_index(text, filename)
                add_bichar_index(text, filename)
    with open(docopt_args['<inv_index_output>'], 'wb') as fout:
        pickle.dump(index_dict, fout)

if __name__ == '__main__':
    main(docopt(__doc__))
