"""
Hard-coded version of experiment_2.ipynb and experiment_2_addon.ipynb.
"""
from __future__ import division
import pandas as pd
from argparse import ArgumentParser
from scipy.stats import ttest_1samp
import re
import logging
import os

def run_compare_test(tweet_data_1, tweet_data_2):
    relevant_users = set(tweet_data_1.loc[:, 'user'].unique()) & set(tweet_data_2.loc[:, 'user'].unique())
    tweet_data_relevant_1 = tweet_data_1[tweet_data_1.loc[:, 'user'].isin(relevant_users)]
    tweet_data_relevant_2 = tweet_data_2[tweet_data_2.loc[:, 'user'].isin(relevant_users)]
    tweet_count_1 = tweet_data_relevant_1.shape[0]
    tweet_count_2 = tweet_data_relevant_2.shape[0]
    user_count = len(relevant_users)
    logging.info('%d tweets in data 1'%(tweet_count_1))
    logging.info('%d tweets in data 2'%(tweet_count_2))
    logging.info('%d relevant users'%(user_count))
    ca_1 = tweet_data_relevant_1.groupby('user').apply(lambda x: (x.loc[:, 'lang']=='ca').astype(int).sum() / x.shape[0])
    ca_2 = tweet_data_relevant_2.groupby('user').apply(lambda x: (x.loc[:, 'lang']=='ca').astype(int).sum() / x.shape[0])
    ca_use_diff = ca_1 - ca_2
    d_u = ca_use_diff.mean()
    N = len(ca_use_diff)
    d_u_err = ca_use_diff.std() / N**.5
    h_0 = 0.
    t_stat, p_val = ttest_1samp(ca_use_diff, h_0)
    logging.info('d_u = %.5f, err = %.5f, t=%.3f (p=%.3E)'%(d_u, d_u_err, t_stat, p_val))
    stats = pd.Series([tweet_count_1, tweet_count_2, user_count], index=['treatment_tweets', 'control_tweets', 'users'])
    results = pd.Series([d_u, d_u_err, t_stat, p_val], index=['d_u', 'd_u_err', 't', 'p'])
    return stats, results

def main():
    parser = ArgumentParser()
    parser.add_argument('--tweet_file', default='../../data/tweets/extra_user_tweets/Jan-01-17_Oct-31-17_user_tweets_final.tsv')
    parser.add_argument('--out_dir', default='../../output')
    args = parser.parse_args()
    tweet_file = args.tweet_file
    out_dir = args.out_dir
    if(not os.path.exists(out_dir)):
        os.mkdir(out_dir)
    logging.basicConfig(level=logging.INFO, filemodel='w', format='%(message)s', filename=os.path.join(out_dir,'experiment_2.txt'))
    stats_out_file = os.path.join(out_dir, 'experiment_2_tweet_user_counts.tsv')
    results_out_file = os.path.join(out_dir, 'experiment_2_results.tsv')
    all_stats = pd.DataFrame()
    all_results = pd.DataFrame()

    ## load data
    tweet_data = pd.read_csv(tweet_file, sep='\t', index_col=False)
    tweet_data.fillna('', inplace=True)
    tweet_data.loc[:, 'hashtag_count'] = tweet_data.loc[:, 'hashtags'].apply(lambda x: 0 if x=='' else len(x.split(',')))
    # tag @-replies
    at_matcher = re.compile('@\w+')
    tweet_data.loc[:, 'reply'] = tweet_data.apply(lambda r: int(len(at_matcher.findall(r.loc['text'])) > 0 and r.loc['retweeted']==0), axis=1)
    # and hashtag counts
    tweet_data.loc[:, 'hashtag_count'] = tweet_data.loc[:, 'hashtags'].apply(lambda x: len(x.split(',')) if x != '' else 0)
    tweet_data_original = tweet_data[tweet_data.loc[:, 'retweeted'] == 0]
    # language cutoff
    lang_conf_cutoff = 0.90
    allowed_langs = set(['es', 'ca'])
    tweet_data_original_high_conf = tweet_data_original[(tweet_data_original.loc[:, 'lang_conf'] >= lang_conf_cutoff) &
                                                        (tweet_data_original.loc[:, 'lang'].isin(allowed_langs))]
    # restrict to relevant users
    relevant_users = tweet_data_original_high_conf.groupby('user').apply(lambda x: (x.loc[:, 'contains_ref_hashtag'].max()==1 and 
                                                                                    x.loc[:, 'contains_ref_hashtag'].min()==0))
    relevant_users = relevant_users[relevant_users].index.tolist()
    tweet_data_relevant = tweet_data_original_high_conf[tweet_data_original_high_conf.loc[:, 'user'].isin(relevant_users)]

    ## split into referendum and control data
    logging.info('starting referendum versus control test')
    tweet_data_ref = tweet_data_relevant[tweet_data_relevant.loc[:, 'contains_ref_hashtag'] == 1]
    tweet_data_control = tweet_data_relevant[tweet_data_relevant.loc[:, 'contains_ref_hashtag'] == 0]

    ### first test: referendum versus non-referendum tweets
    ## compute probability of Catalan in referendum and control tweets
    stats, results = run_compare_test(tweet_data_ref, tweet_data_control)
    all_stats = all_stats.append(pd.DataFrame(stats).transpose())
    all_results = all_results.append(pd.DataFrame(results).transpose())

    ### second test: referendum versus non-referendum tweets with hashtags
    logging.info('starting referendum versus hashtag control test')

    ## re-segment data, relevant users
    tweet_data_with_hashtags = tweet_data_original_high_conf[tweet_data_original_high_conf.loc[:, 'hashtag_count'] > 0]
    relevant_users = tweet_data_with_hashtags.groupby('user').apply(lambda x: (x.loc[:, 'contains_ref_hashtag'].max()==1 and 
                                                                               x.loc[:, 'contains_ref_hashtag'].min()==0))
    relevant_users = relevant_users[relevant_users].index.tolist()
    tweet_data_relevant_with_hashtags = tweet_data_with_hashtags[tweet_data_with_hashtags.loc[:, 'user'].isin(relevant_users)]
    tweet_data_ref = tweet_data_relevant_with_hashtags[tweet_data_relevant_with_hashtags.loc[:, 'contains_ref_hashtag'] == 1]
    tweet_data_control = tweet_data_relevant_with_hashtags[tweet_data_relevant_with_hashtags.loc[:, 'contains_ref_hashtag'] == 0]
    stats, results = run_compare_test(tweet_data_ref, tweet_data_control)
    all_stats = all_stats.append(pd.DataFrame(stats).transpose())
    all_results = all_results.append(pd.DataFrame(results).transpose())

    ## third test: @-replies versus non-replies with hashtag
    logging.info('starting reply versus not-reply test')
    reply_data = tweet_data_original_high_conf[(tweet_data_original_high_conf.loc[:, 'reply']==1) & (tweet_data_original_high_conf.loc[:, 'hashtag_count']==0)]
    hashtag_data = tweet_data_original_high_conf[(tweet_data_original_high_conf.loc[:, 'reply']==0) & (tweet_data_original_high_conf.loc[:, 'hashtag_count']>0)]
    stats, results = run_compare_test(reply_data, hashtag_data)
    all_stats = all_stats.append(pd.DataFrame(stats).transpose())
    all_results = all_results.append(pd.DataFrame(results).transpose())
    
    ## write stats, results to file
    all_stats.loc[:, 'condition'] = ['hashtags_vs_all', 'hashtags_vs_hashtags', 'replies_vs_all']
    all_results.loc[:, 'condition'] = ['hashtags_vs_all', 'hashtags_vs_hashtags', 'replies_vs_all']
    all_stats.transpose().to_csv(stats_out_file, sep='\t', index=True, header=False)
    all_results.transpose().to_csv(results_out_file, sep='\t', index=True, header=False)

if __name__ == '__main__':
    main()
