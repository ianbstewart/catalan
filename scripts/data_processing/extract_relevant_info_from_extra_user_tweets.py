"""
Extract username, text, hashtags, and pro/anti label
for all extra user tweets.
"""
import pandas as pd
from langid import classify
import re
from argparse import ArgumentParser
import codecs
import json

def main():
    parser = ArgumentParser()
    parser.add_argument('--user_tweet_file', default='../../data/tweets/extra_user_tweets/Jan-01-17_Oct-31-17_user_tweets.json')
    # parser.add_argument('--pro_anti_file', default='../../data/referendum_hashtags.csv')
    parser.add_argument('--expanded_hashtag_file', default='../../data/expanded_fixed_hashtags.csv')
    args = parser.parse_args()
    user_tweet_file = args.user_tweet_file
    # pro_anti_file = args.pro_anti_file
    expanded_hashtag_file = args.expanded_hashtag_file
    
    ## load data
    # pro_anti_hashtags = pd.read_csv(pro_anti_file, sep=',', index_col=False)
    expanded_hashtags = pd.read_csv(expanded_hashtag_file, sep=',', index_col=False).loc[:, 'expanded']
    expanded_hashtag_set = set(expanded_hashtags)
    # print(expanded_hashtag_set)
    # remapping
    
    ## process data
    data = []
    hashtag_matcher = re.compile('(?<=#)[^# ]+')
    rt_matcher = re.compile('^rt[ :]')
    space_matcher = re.compile('(\s+|\n|\t)')
    # cutoff = 10000
    with codecs.open(user_tweet_file, 'r', encoding='utf-8') as user_tweet_input:
        for i, l in enumerate(user_tweet_input):
            l = l.strip()
            try:
                t = json.loads(l)
                # remove spaces
                t_text = space_matcher.sub(' ',t['text'])
                t_hashtags = hashtag_matcher.findall(t_text)
                t_contains_ref_hashtag = int(len(set(t_hashtags) & expanded_hashtag_set) > 0)
                t_lang, t_lang_conf = classify(t_text)
                t_is_rt = int(len(rt_matcher.findall(t_text.lower())) > 0)
                t_data = [t['id'], t['user']['screen_name'], t_text, ','.join(t_hashtags), t_contains_ref_hashtag, t_lang, t_lang_conf, t_is_rt]
                data.append(t_data)
                # extract hashtags
            except Exception, e:
                pass
            if(i % 100000 == 0):
                print('processed %d tweets'%(i))
    col_names = ['id', 'user', 'text', 'hashtags', 'contains_ref_hashtag', 'lang', 'lang_conf', 'retweeted']
    data = pd.DataFrame(data, columns=col_names)
    
    ## write to file
    out_file_name = user_tweet_file.replace('.json', '.tsv')
    data.to_csv(out_file_name, sep='\t', index=False, encoding='utf-8')
    
if __name__ == '__main__':
    main()
