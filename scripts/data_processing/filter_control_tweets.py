"""
Filter control tweets to only include tweets actually
written by referendum authors of interest
(because when we mined control tweets,
we extracted all tweets that included authors somewhere in tweet).
"""
import argparse
import pandas as pd
import logging

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--control_data_file', default='../../data/tweets/extra_user_tweets/Jan-01-17_Oct-31-17_user_tweets.tsv')
    parser.add_argument('--user_group_file', default='../../data/user_groups.csv')
    args = parser.parse_args()
    control_data_file = args.control_data_file
    user_group_file = args.user_group_file
    logging.basicConfig(filename='../../output/filter_control_tweets.txt', filemode='w', level=logging.INFO)

    ## load data
    control_data = pd.read_csv(control_data_file, sep='\t', index_col=False)
    user_groups = pd.read_csv(user_group_file, sep=',', index_col=False)
    relevant_users = user_groups.loc[:, 'username'].values
    
    ## filter data
    control_data = control_data[control_data.loc[:, 'user'].isin(relevant_users)]
    logging.debug('%d control tweets'%(control_data.shape[0]))
    
    ## write to file
    out_file = control_data_file.replace('.tsv', '_final.tsv')
    control_data.to_csv(out_file, sep='\t', index=False)

if __name__ == '__main__':
    main()
