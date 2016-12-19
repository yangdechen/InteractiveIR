# File name: gen_simulate_keyword.py
# Author: Yang-de Chen
# Date created: 12/14/2016
# Date modified: 12/19/2016
# python version: 3.5+
# Description:
#   Generate releated keyword for each keyword for simulation.
'''Generate Keyword for simulation

Usage:
    gen_simulate_keyword.py <ptv-ans> <doc-dir> <output>
    gen_simulate_keyword.py -h
Options:
    -h --help       : show help messages
'''
import os
import sys
from docopt import docopt
from collections import defaultdict

# TODO: Obviously, this is not very reasonable. Refine this so that it can
# generate more sensible simulation.
def main(docopt_args):
    '''
    For each keyword, generate related keywords if it appears in more than
    half of the documents.
    '''
    with open(docopt_args['<ptv-ans>']) as ans_file:
        with open(docopt_args['<output>'], 'w') as out_file:
            for line in ans_file:
                query, *ans = line.strip().split()
                num_ans = len(ans)
                word_count = defaultdict(int)
                for doc in ans:
                    doc_set = set()
                    with open(os.path.join(docopt_args['<doc-dir>'],
                                           doc)) as f:
                        for doc_line in f:
                            for word in doc_line.strip().split():
                                doc_set.add(word)
                    for word in doc_set:
                        word_count[word] += 1
                word_list = []
                for word, count in word_count.items():
                    # appear in more than half of the documents
                    if count > num_ans / 2:
                        word_list.append(word)
                out_file.write('{0} {1}\n'.format(query, ' '.join(word_list)))

if __name__ == '__main__':
    main(docopt(__doc__))
