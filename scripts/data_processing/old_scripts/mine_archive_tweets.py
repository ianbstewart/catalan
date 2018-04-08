"""
Mine the local Twitter archive
for specified hashtags.
"""
import os
import json
from argparse import ArgumentParser
import pandas as pd
import codecs
from dateutil.parser import parse
from datetime import timedelta
from datetime import datetime
import re
import gzip
import sys
from unidecode import unidecode
# suppress unidecode warning
import warnings
# def warning_func():
#     warnings.warn('RuntimeWarning', RuntimeWarning)
# with warnings.catch_warnings():
#     warnings.simplefilter('ignore')
#     warning_func()
warnings.filterwarnings('ignore')

SPACE_MATCHER = re.compile('\t|\n')
clean_txt = lambda x: SPACE_MATCHER.sub(' ', x)
def mine_tweets(tweet_file_name, hashtag, out_file):
    data_vars = ['date', 'favorites', 'geo', 'hashtags', 'id', 'mentions', 'permalink', 'retweets', 'text', 'screen_name']
    entity_vars = ['hashtags', 'user_mentions']
    social_vars = ['favorite_count', 'retweet_count']
    data_var_rename_lookup = {'favorite_count' : 'favorites', 
                              'retweet_count' : 'retweets',
                              'created_at' : 'date',
                              'user_mentions' : 'mentions'}
    permalink_builder = 'https://twitter.com/%s/status/%s'
#     with codecs.open(out_file_name, 'w', encoding='utf-8') as output_file:
    decode_txt = lambda x: unidecode(x)
    hashtag_no_accent = decode_txt(hashtag.decode('utf-8'))
    hashtag_lower = hashtag.lower()
    hashtag_lower_no_accent = decode_txt(hashtag_lower.decode('utf-8'))
    hashtag_list = [hashtag, hashtag_no_accent, hashtag_lower, hashtag_lower_no_accent]
    hashtag_matcher = re.compile('|'.join(map(lambda x: '#%s'%(x), hashtag_list)))
    tweet_ctr = 0
    for l in gzip.open(tweet_file_name, 'r'):
        try:
            tweet = json.loads(l.strip())
            # test for deletion
            if(tweet.get('delete') is None and tweet.get('status_withheld') is None):
                # check for hashtag in text!
                # TODO: more graceful way of matching on hashtags
                if(tweet.get('text') is not None and len(hashtag_matcher.findall(tweet['text'])) > 0):
                    # extract entity vars
                    if(tweet.get('entities') is not None):
                        for e_v in entity_vars:
                            tweet[e_v] = tweet['entities'][e_v]
                    # attempt to extract social vars
                    for v in social_vars:
                        if(tweet.get(v) is None):
                            v_fixed = v.replace('_count', 's')
                            if(tweet.get(v_fixed) is not None):
                                tweet[v] = tweet[v_fixed]
                            else:
                                tweet[v] = 0
                    # extract user name
                    tweet['screen_name'] = tweet['user']['screen_name']
                    # build permalink
                    tweet['permalink'] = permalink_builder%(tweet['screen_name'], tweet['id_str'])
                    # clean text
                    tweet['text'] = clean_txt(tweet['text'])
                    # rename keys
                    for v1, v2 in data_var_rename_lookup.iteritems():
                        tweet[v2] = tweet[v1]
                        del(tweet[v1])
                    # collect data
                    tweet_line = ['%s'%(tweet[v]) for v in data_vars]
                    # write!!
                    out_file.write('\t'.join(tweet_line))
                    tweet_ctr += 1
                    if(tweet_ctr % 100 == 0):
                        print('collected %d tweets'%(tweet_ctr))
        except Exception, e:
            try:
                print(json.dumps(tweet, indent=2))
            except Exception, e1:
                pass
            exc_type, exc_obj, tb = sys.exc_info()
            print('passing tweet at line %d because:\n%s'%(tb.tb_lineno, e))
            pass

def main():
    parser = ArgumentParser()
    parser.add_argument('--archive_dir', default='/hg190/corpora/twitter-crawl/new-archive/')
#     parser.add_argument('--hashtags', nargs= default='')
    parser.add_argument('--hashtag_file', default='../../data/referendum_hashtags.csv')
    parser.add_argument('--start_date', default='Sep-01-17')
    parser.add_argument('--end_date', default='Nov-01-17')
    parser.add_argument('--out_dir', default='../../data/tweets')
    args = parser.parse_args()
    archive_dir = args.archive_dir
    hashtag_file = args.hashtag_file
    start_date_str = args.start_date
    end_date_str = args.end_date
    out_dir = args.out_dir
    
    ## load hashtags
    hashtags = pd.read_csv(hashtag_file, header=0).loc[:, 'hashtag'].values.tolist()
    
    ## collect files
    start_date = parse(start_date_str)
    end_date = parse(end_date_str)
    day_count = (end_date - start_date).days
    date_range = [end_date - timedelta(days=x) for x in range(day_count)][::-1]
    tweet_file_base = 'tweets-%s-[0-9]{2}-[0-9]{2}.gz'
    date_fmt = '%b-%d-%y'
    generate_file_name = lambda d: tweet_file_base%(datetime.strftime(d, date_fmt))
    tweet_files = reduce(lambda x,y: x+y, [[os.path.join(archive_dir, f) for f in os.listdir(archive_dir) if re.compile(generate_file_name(d)).match(f)] for d in date_range])

    ## mine
    out_file_base = os.path.join(out_dir, '%s_%s_%s_archive.tsv'%('%s', start_date_str, end_date_str))
    for hashtag in hashtags:
        out_file_name = out_file_base%(hashtag)
        print(out_file_name)
        with codecs.open(out_file_name, 'w', encoding='utf-8') as out_file:
            for tweet_file in tweet_files:
                print('processing file %s'%(tweet_file))
                mine_tweets(tweet_file, hashtag, out_file)
    
if __name__ == '__main__':
    main()