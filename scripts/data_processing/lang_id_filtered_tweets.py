"""
Apply lang ID to filtered tweets.
"""
import json
from langid import classify
from argparse import ArgumentParser
import codecs
import pandas as pd

def main():
    parser = ArgumentParser()
    parser.add_argument('--filtered_tweet_file', default='../../data/tweets/archive_Jan-01-17_Oct-31-17_ref_hashtags_filtered.json')
    args = parser.parse_args()
    filtered_tweet_file = args.filtered_tweet_file

    ## load data
    tweet_data = [json.loads(t) for t in codecs.open(filtered_tweet_file, 'r', encoding='utf-8')]
    
    ## classify
    lang_ids = map(lambda x: classify(x['text']), tweet_data)
    # reshape data
    tweet_data_df = pd.DataFrame()
    tweet_data_df.loc[:, 'id'] = map(lambda t: t['id'], tweet_data)
    langs, confs = zip(*lang_ids)
    tweet_data_df.loc[:, 'lang'] = langs
    tweet_data_df.loc[:, 'conf'] = confs
    
    ## write to file
    out_file_name = filtered_tweet_file.replace('.json', '_langid.csv')
    print(out_file_name)
    tweet_data_df.to_csv(out_file_name, index=False)

if __name__ == '__main__':
    main()
