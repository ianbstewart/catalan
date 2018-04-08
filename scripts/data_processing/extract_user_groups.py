"""
Extract pro/anti users from filtered tweets.
"""
from __future__ import unicode_literals, division
import json
from collections import Counter, defaultdict
import pandas as pd
from argparse import ArgumentParser

def main():
  parser = ArgumentParser()
  parser.add_argument('--expanded_hashtag_file', default='../../data/expanded_hashtags.csv')
  parser.add_argument('--fixed_hashtag_file', default='../../data/expanded_fixed_hashtags.csv')
  parser.add_argument('--filtered_tweet_file', default='../../data/tweets/archive_Jan-01-17_Oct-31-17_ref_hashtags_filtered.json')
  parser.add_argument('--out_file', default='../../data/user_groups.csv')
  args = parser.parse_args()
  expanded_hashtag_file = args.expanded_hashtag_file
  fixed_hashtag_file = args.fixed_hashtag_file
  filtered_tweet_file = args.filtered_tweet_file
  out_file = args.out_file
  
  ## load data
  base_ht_df = pd.read_csv(expanded_hashtag_file, encoding='UTF8')
  exp_ht_df = pd.read_csv(fixed_hashtag_file, encoding='UTF8')

  ## get pro/anti tags
  all_ht_df = base_ht_df.merge(exp_ht_df, how='outer', left_on='hashtag', right_on='original')
  pro_tags = [h.strip() for h in all_ht_df[all_ht_df.sentiment == 'pro']['expanded']]
  anti_tags = [h.strip() for h in all_ht_df[all_ht_df.sentiment == 'anti']['expanded']]
  
  ## get user counts
  
  dec = json.JSONDecoder()
  user_counts = defaultdict(Counter)
  with open(filtered_tweet_file) as json_file:
      for l in json_file:
          record = dec.decode(l)
          hashtags = [t.strip()[1:] for t in record['text'].split() if t.startswith('#')]
          pro_ct = len([h for h in hashtags if h in pro_tags])
          anti_ct = len([h for h in hashtags if h in anti_tags])
          if pro_ct > 0:
              user_counts[record['user']]['pro'] += 1
          if anti_ct > 0:
              user_counts[record['user']]['anti'] += 1

  def pro_rate(user_ct):
      return user_ct['pro'] / sum(user_ct.values())

  pro_users = [u for u,c in user_counts.items() if pro_rate(c) >= 0.75]
  anti_users = [u for u,c in user_counts.items() if pro_rate(c) <= 0.25]

  ## write to file
  out_df = pd.concat([pd.DataFrame(data={'username':pro_users, 'group':'YES'}),
                    pd.DataFrame(data={'username':anti_users, 'group':'NO'})])
  out_df.to_csv(out_file, index=False, encoding='UTF8')
  
if __name__ == '__main__':
  main()
