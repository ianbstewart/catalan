"""
Remove all tweets authored by users
who mostly (>90th percentile) post
tweets with URLs.
"""
from __future__ import division
import json
from argparse import ArgumentParser
from collections import defaultdict
import codecs
import re
import pandas as pd
from collections import Counter
import os
import logging

def main():
    parser = ArgumentParser()
    parser.add_argument('--tweet_file', default='../../data/tweets/archive_Jan-01-17_Oct-31-17_ref_hashtags.json')
    parser.add_argument('--hashtag_file', default='../../data/expanded_fixed_hashtags.csv')
    parser.add_argument('--out_dir', default='../../data/tweets')
    args = parser.parse_args()
    tweet_file = args.tweet_file
    hashtag_file = args.hashtag_file
    out_dir = args.out_dir
    file_prefix = os.path.basename(tweet_file).replace('.json','')

    log_file_name = os.path.join(out_dir, 'filter_tweets_for_spam.log')
    logging.basicConfig(filename=log_file_name,
                        filemode='w',
                        # format='%(asctime)s %(levelname)s %(message)s',
                        format='%(message)s',
                        level=logging.INFO)

    ## load data
    tweet_data = []
    cutoff = 10000
    for i, l in enumerate(codecs.open(tweet_file, 'r', encoding='utf-8')):
        try:
            j = json.loads(l)
            # limit to relevant data!
            j_relevant = {'user' : j['user']['screen_name'], 'text' : j['text'], 
                          'date' : j['created_at'], 'id' : j['id'], 
                          'location.name' : '', 'location.country' : ''}
            # extract retweet??
            if(j.get('location') is not None and j.get('location').get('place') is not None):
                j_place = j['location']['place']
                j_relevant['location.name'] = j_place['full_name']
                j_relevant['location.country'] = j_place['country']
            tweet_data.append(j_relevant)
        except Exception, e:
            pass
        if(i % 10000 == 0):
            logging.info('processed %d tweets'%(i))
            #print('processed %d tweets'%(i))
        #if(i > cutoff):
        #    break
    logging.info('%d total tweets to start'%(len(tweet_data)))
    #print('%d total tweets to start'%(len(tweet_data)))
    tweet_data_users = set([t['user'] for t in tweet_data])
    logging.info('%d total users'%(len(tweet_data_users)))
    # print('%d total users'%(len(tweet_data_users)))
    
    ## zero pass: make sure tweet contains at least one referendum hashtag
    hashtags = pd.read_csv(hashtag_file, sep=',', index_col=False).loc[:, 'expanded'].values.tolist()
    # make them hashtags
    hashtags = map(lambda x: '#%s'%(x), hashtags)
    hashtag_matcher = re.compile('|'.join(hashtags))
    invalid_tweet_data = filter(lambda j: len(hashtag_matcher.findall(j['text'])) == 0, tweet_data)
    tweet_data = filter(lambda j: len(hashtag_matcher.findall(j['text'])) > 0, tweet_data)
    tweet_data_users = set([t['user'] for t in tweet_data])
    logging.info('%d valid tweets with %d users'%(len(tweet_data), len(tweet_data_users)))
    # print('%d valid tweets with %d users'%(len(tweet_data), len(tweet_data_users)))
    # examples of invalid tweets?
    logging.info('invalid tweet examples')
    logging.info('\n'.join([t['text'] for t in invalid_tweet_data[:20]]))
    # print('invalid tweet examples')
    # print('\n'.join([t['text'] for t in invalid_tweet_data[:20]]))
    # write to file
    original_data_file = os.path.join(out_dir, '%s_original.json'%(file_prefix))
    with codecs.open(original_data_file, 'w', encoding='utf-8') as original_data_output:
        for t in tweet_data:
            original_data_output.write('%s\n'%(json.dumps(t)))

    ## first pass: get rid of RTs
    rt_matcher = re.compile('^rt[ :]')
    tweet_data = filter(lambda j: len(rt_matcher.findall(j['text'].lower())) == 0, tweet_data)
    tweet_data_users = set([t['user'] for t in tweet_data])
    logging.info('%d original tweets with %d users'%(len(tweet_data), len(tweet_data_users)))
    # print('%d original tweets with %d users'%(len(tweet_data), len(tweet_data_users)))
    # write to file
    original_data_file = os.path.join(out_dir, '%s_original.json'%(file_prefix))
    with codecs.open(original_data_file, 'w', encoding='utf-8') as original_data_output:
        for t in tweet_data:
            original_data_output.write('%s\n'%(json.dumps(t)))
    # print('\n'.join([t['text'] for t in tweet_data[:10]]))

    ## second pass: get rid of high-URL users
    user_url_counts = Counter()
    user_tweet_counts = Counter()
    URL_MATCHER = re.compile('https?://|twitter.com/')
    for j in tweet_data:
        j_txt = j['text']
        j_user = j['user']
        user_tweet_counts[j_user] += 1
        if(len(URL_MATCHER.findall(j['text'])) > 0):
            user_url_counts[j_user] += 1
    # normalize
    user_tweet_counts = pd.Series(user_tweet_counts)
    user_url_counts = pd.Series(user_url_counts)
    user_url_pcts = user_url_counts / user_tweet_counts.loc[user_url_counts.index]
    # compute 90th percentile
    pct = 90
    pct_cutoff = pd.np.percentile(user_url_pcts, pct)
    logging.info('%d percentile of URL counts = %.3f'%(pct, pct_cutoff))
    logging.info('%d high-URL users'%(len(user_url_pcts[user_url_pcts >= pct_cutoff])))
    # print('%d percentile of URL counts = %.3f'%(pct, pct_cutoff))
    # print('%d high-URL users'%(len(user_url_pcts[user_url_pcts >= pct_cutoff])))
    # remove users with high URL percentage
    # tweet cutoff is too high, only filters a few users
    #tweet_cutoff = 5
    tweet_cutoff = 3
    # tweet count and url pct
    filtered_users = (user_tweet_counts[user_tweet_counts >= tweet_cutoff].index & 
                      user_url_pcts[user_url_pcts >= pct_cutoff].index)
    # url pct
    # filtered_users = user_url_pcts[user_url_pcts >= pct_cutoff].index
    filtered_user_tweets = user_tweet_counts.loc[filtered_users].sum()
    logging.info('filtering %d users with %d tweets'%(len(filtered_users), filtered_user_tweets))
    # print('filtering %d users with %d tweets'%(len(filtered_users), filtered_user_tweets))
    filtered_user_set = set(filtered_users)
    tweet_data = filter(lambda x: x['user'] not in filtered_user_set, tweet_data)
    tweet_data_users = set([t['user'] for t in tweet_data])
    logging.info('%d tweets with %d users'%(len(tweet_data), len(tweet_data_users)))
    # print('%d tweets with %d users'%(len(tweet_data), len(tweet_data_users)))
    # write to file
    filtered_data_file = os.path.join(out_dir, '%s_filtered.json'%(file_prefix))
    with codecs.open(filtered_data_file, 'w', encoding='utf-8') as filtered_data_output:
        for t in tweet_data:
            filtered_data_output.write('%s\n'%(json.dumps(t)))

if __name__ == '__main__':
    main()
        
