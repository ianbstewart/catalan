"""
Get user tweet counts from archive data.
We need this to filter high-volume posters.
"""
import gzip
import json
from collections import Counter
from argparse import ArgumentParser
import re
import pandas as pd

def main():
    parser = ArgumentParser()
    parser.add_argument('archive_files', nargs='+')
    parser.add_argument('--out_file', default='../../data/tweets/user_tweet_counts.csv')
    args = parser.parse_args()
    archive_files = args.archive_files
    out_file = args.out_file
    rt_matcher = re.compile('rt[ :]')
    user_tweet_counts = Counter()
#    cutoff = 100000
    ctr = 0
    for f in archive_files:
        print('processing file %s'%(f))
        with gzip.open(f, 'r') as f_input:
            for l in f_input:
                l = l.strip()
                try:
                    j = json.loads(l)
                    j_txt = j.get('text')
                    if(j_txt is not None and j.get('user') is not None):
                        if(len(rt_matcher.findall(j_txt)) == 0):
                            j_user = j['user']['screen_name']
                            user_tweet_counts[j_user] += 1
                except Exception, e:
                    pass
                ctr += 1
                if(ctr % 1000000 == 0):
                    print('processed %d tweets'%(ctr))
                #if(ctr > cutoff):
                #    break
    user_tweet_counts = pd.Series(user_tweet_counts)
    # limit to high-count users
    tweet_cutoff = 5
    user_tweet_counts = user_tweet_counts[user_tweet_counts >= tweet_cutoff]
    user_tweet_counts.to_csv(out_file)

if __name__ == '__main__':
    main()
