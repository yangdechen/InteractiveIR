# File name: calc_doc_len.py
# Author: Yang-de Chen
# Date created: 12/14/2016
# Date modified: 12/19/2016
# python version: 3.5+
# Description:
#   Run interactive retrieval experiment.
"""calc_doc_len.py
    
Usage:
    calc_doc_len.py <dirname> <doclen_out>
    calc_doc_len.py -h

Options:
    -h --help       : show help message
"""
import sys
import pickle
from docopt import docopt
from util import walk_all_files

len_dict = dict()
def main(docopt_args):
    all_files = walk_all_files(docopt_args['<dirname>'])
    for filename, filepath, in all_files:
        doclen = 0
        with open(filepath) as f:
            for line in f:
                text = ''.join(line.strip().split())
                doclen += len(text)
        len_dict[filename] = doclen

    with open(docopt_args['<doclen_out>'], 'wb') as f:
        pickle.dump(len_dict, f)

if __name__ == '__main__':
    main(docopt(__doc__))
