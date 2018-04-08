#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mine historical Twitter data
for specific hashtags.
"""
import sys
if('GetOldTweets' not in sys.path):
    sys.path.append('GetOldTweets')
import got
from argparse import ArgumentParser
import pandas as pd
import os
import re

def mine_for_hashtags(hashtags, start_date, end_date):
    """
    Mine for all tweets containing at least one
    of the specified hashtags in the timespan.
    
    Parameters:
    -----------
    hashtags : list
    start_date : str
    end_date : str
    
    Returns:
    --------
    tweets : list
    """
    hashtags_str = ' '.join(map(lambda x: '#%s'%(x), hashtags))
    tweetCriteria = got.manager.TweetCriteria().setQuerySearch(hashtags_str)
    tweetCriteria.setSince(start_date)
    tweetCriteria.setUntil(end_date)
    try:
        tweets = got.manager.TweetManager.getTweets(tweetCriteria)
    except Exception, e:
        print('halting mine because of exception %s'%(e))
        tweets = []
    return tweets

## TODO: rewrite the mining code to dump directly to file instead of storing in memory
def main():
    parser = ArgumentParser()
    # hard-coding hashtags
#     parser.add_argument('--hashtags', nargs='+', default=['CataluñaLibre'])
    # loading hashtags from file
    parser.add_argument('--hashtag_file', default='../../data/referendum_hashtags.csv')
    parser.add_argument('--start_date', default='2017-09-01')
    parser.add_argument('--end_date', default='2017-11-01')
    parser.add_argument('--out_dir', default='../../data/tweets/')
    args = parser.parse_args()
#     hashtags = args.hashtags
    hashtag_file = args.hashtag_file
    start_date = args.start_date
    end_date = args.end_date
    out_dir = args.out_dir
    
    ## load hashtags
    hashtags = pd.read_csv(hashtag_file, index_col=False).loc[:, 'hashtag'].values.tolist()
    
    ## mine
    for hashtag in hashtags:
        print('mining hashtag %s'%(hashtag))
        tweets = mine_for_hashtags([hashtag], start_date, end_date)
        print('collected %d tweets'%(len(tweets)))
        if(len(tweets) > 0):
            ## convert data and write to file
            tweet_vals = map(vars, tweets)
            tweet_df = pd.concat(map(pd.Series, tweet_vals), axis=1).transpose()
            # clean text
            space_matcher = re.compile('\t|\n')
            clean_txt = lambda x: space_matcher.sub(' ', x)
            tweet_df.loc[:, 'text'] = tweet_df.loc[:, 'text'].apply(clean_txt)
    #         hashtag_str = ','.join(hashtags)
            out_file_name = os.path.join(out_dir, '%s_%s_%s.tsv'%(hashtag, start_date, end_date))
            tweet_df.to_csv(out_file_name, sep='\t', index=False, encoding='utf-8')
    
if __name__ == '__main__':
    main()
