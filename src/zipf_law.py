# File name: zipf_law.py
# Date created: 12/23/2016
# Date modified: 12/23/206
# python version: 3.5+
# Description:
#   corpus statistics for stopword removal
'''zipf_law.py

Usage:
    zipf_law.py <corpus-dir>
    zipf_law.py -h

Options:
    -h --help   : show help messages
'''
from docopt import docopt
from operator import itemgetter
from collections import defaultdict
from util import walk_all_files
from math import log

def main(docopt_args):
    tf_stats = defaultdict(int)
    df_stats = defaultdict(int)
    corpus_dir = docopt_args['<corpus-dir>']
    for filename, filepath in walk_all_files(corpus_dir):
        with open(filepath) as infile:
            tf_dict = defaultdict(int)
            counts = 0
            for line in infile:
                for word in line.strip().split():
                    tf_dict[word] += 1
                    counts += 1
            for word in tf_dict:
                df_stats[word] += 1
                tf_stats[word] += tf_dict[word] / counts
    merge_stats = {}
    for word in tf_stats:
        merge_stats[word] = log(1 + tf_stats[word]) * log(1 + df_stats[word])
    merge_stats_sorted = sorted(merge_stats.items(), key=itemgetter(1), reverse=True)
    for word, score in merge_stats_sorted:
        print(word, score)

if __name__ == '__main__':
    main(docopt(__doc__))
