# File name: main.py
# Author: Yang-de Chen
# Date created: 12/14/2016
# Date modified: 12/18/2016
# python version: 3.5+
# Description:
#   Run interactive retrieval experiment.
'''main

Usage:
    main.py <flag> <ptv-query> <ptv-ans> <inv-index> <doc-len> <bg-lm>
            <keyword-dir> <doc-dir> <sim_keyword_file> <model>
    main.py -h
Options:
    -h --help       : show help messages
'''
from docopt import docopt
from agent import Agent
from environment import IIREnvironment
import pickle

def main(docopt_args):
    '''Experiment setup'''
    env = IIREnvironment(
        query_file=docopt_args['<ptv-query>'],
        ans_file=docopt_args['<ptv-ans>'],
        index_file=docopt_args['<inv-index>'],
        doclen_file=docopt_args['<doc-len>'],
        bglm_file=docopt_args['<bg-lm>'],
        keyword_dirname=docopt_args['<keyword-dir>'],
        doc_dir=docopt_args['<doc-dir>'],
        sim_keyword_file=docopt_args['<sim_keyword_file>'],
        max_queries=5,      # maximum number of queries a user can hold
        patience_mean=5,
        patience_std=2,
        patience_min=1,
        ap_thres_mean=0.7,
        ap_thres_std=0.1,
        ap_thres_min=0.1)
    agent = Agent(
        env=env,
        history_len=5,
        train_pool_size=64,
        allowed_feedback_pos=5,
        feedback_weight=1,
        like_weight=1)

    if docopt_args['<flag>'] == 'train':
        agent.play(n_episodes=100, isTraining=True)
        with open(docopt_args['<model>'], 'wb') as f:
            pickle.dump(agent.strategy, f)
    elif docopt_args['<flag>'] == 'test':
        with open(docopt_args['<model>'], 'rb') as f:
            agent.strategy = pickle.load(f)
        agent.play(n_episodes=100, isTraining=False)

if __name__ == '__main__':
    main(docopt(__doc__))
