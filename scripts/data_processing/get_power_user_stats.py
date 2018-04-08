"""
Compute basic stats on "power users"
in the referendum and control data.
"""
import pandas as pd
import json
import os
from argparse import ArgumentParser
import logging

def main():
    parser = ArgumentParser()
    parser.add_argument('--ref_tweet_file', default='../../data/tweets/archive_Jan-01-17_Oct-31-17_ref_hashtags_filtered.json')
    parser.add_argument('--control_tweet_file', default='../../data/tweets/extra_user_tweets/Jan-01-17_Oct-31-17_user_tweets_final.tsv')
    parser.add_argument('--out_dir', default='../../output')
    args = parser.parse_args()
    ref_tweet_file = args.ref_tweet_file
    control_tweet_file = args.control_tweet_file
    out_dir = args.out_dir
    log_file = os.path.join(out_dir,'power_user_stats.txt')
    if(os.path.exists(log_file)):
        os.remove(log_file)
    logging.basicConfig(level=logging.INFO, filemodel='w', format='%(message)s', filename=log_file)
    

    ## load data
    ref_tweet_data = [json.loads(l.strip()) for l in open(ref_tweet_file)]
    ref_tweet_data = pd.concat([pd.Series(x) for x in ref_tweet_data], axis=1).transpose()
    control_tweet_data = pd.read_csv(control_tweet_file, sep='\t', index_col=False)
    
    ## get user counts
    ref_tweet_user_counts = ref_tweet_data.loc[:, 'user'].value_counts()
    control_tweet_user_counts = control_tweet_data.loc[:, 'user'].value_counts()

    ## get power user stats
    logging.info('ref tweets: %d tweets max'%(ref_tweet_user_counts.max()))
    logging.info('ref tweets: >10 tweets = %d users'%(len(ref_tweet_user_counts[ref_tweet_user_counts > 10])))
    logging.info('ref tweets: >5 tweets = %d users'%(len(ref_tweet_user_counts[ref_tweet_user_counts > 5])))
    logging.info('control tweets: %d tweets max'%(control_tweet_user_counts.max()))
    logging.info('control tweets: >1000 tweets = %d users'%(len(control_tweet_user_counts[control_tweet_user_counts > 1000])))
    logging.info('control tweets: >100 tweets = %d users'%(len(control_tweet_user_counts[control_tweet_user_counts > 100])))

if __name__ == '__main__':
    main()
