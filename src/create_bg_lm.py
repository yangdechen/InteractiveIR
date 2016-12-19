# File name: create_bg_lm.py
# Author: Yang-de Chen
# Date created: 12/14/2016
# Date modified: 12/18/2016
# python version: 3.5+
# Description:
#   Create background language model.
"""create_bg_lm.py
    
Usage:
    create_bg_lm.py <corpus_dir> <bg_lm_output>
    create_bg_lm.py -h
Options:
    -h --help       : show help message
"""
import re
import sys
import pickle
from docopt import docopt
from util import walk_all_files

lm_dict = dict()
char_dict = dict()
bichar_dict = dict()

def main(docopt_args):
    total_char = 0
    total_bichar = 0
    for filename, filepath in walk_all_files(docopt_args['<corpus_dir>']):
        with open(filepath) as f:
            for line in f:
                text = ''.join(line.strip().split())
                for ch in text:
                    char_dict[ch] = char_dict.get(ch, 0) + 1
                    total_char += 1
                for i in range(1, len(text)):
                    bichar = text[i-1] + text[i]
                    bichar_dict[bichar] = bichar_dict.get(bichar, 0) + 1
                    total_bichar += 1
                # normalize the frequency
    for ch in char_dict:
        char_dict[ch] = char_dict[ch] / total_char
    for bichar in bichar_dict:
        bichar_dict[bichar] = bichar_dict[bichar] / total_bichar
    lm_dict = char_dict.copy()
    lm_dict.update(bichar_dict)
    with open(docopt_args['<bg_lm_output>'], 'wb') as fout:
        pickle.dump(lm_dict, fout)

if __name__ == '__main__':
    main(docopt(__doc__))
