"""
Preprocess expanded hashtags for
easy searching.
"""
import unicodedata
from argparse import ArgumentParser
import pandas as pd

def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')

def fix_hashtag(h):
    hashtag_set = set([h])
    h_lower = h.lower()
    # add non-accent versions
    h_unicode = unicode(h.decode('utf-8'))
    h_stripped = strip_accents(h_unicode)
    h_stripped_lower = h_stripped.lower()
    hashtag_set.update([h_lower, h_stripped,h_stripped_lower])
    hashtag_list = list(hashtag_set)
    return hashtag_list

def main():
    parser = ArgumentParser()
    parser.add_argument('--hashtag_file', default='../../data/expanded_hashtags.csv')
    parser.add_argument('--out_file', default='../../data/expanded_fixed_hashtags.csv')
    args = parser.parse_args()
    hashtag_file = args.hashtag_file
    out_file_name = args.out_file
    ## load and convert
    original_hashtags = pd.read_csv(hashtag_file, index_col=False).loc[:, 'hashtag']
    expanded_hashtags = map(lambda x: [x, fix_hashtag(x)], original_hashtags)
    ## convert to data frame
    expanded_hashtags = reduce(lambda x,y: x+y, [[[h, h_variant] for h_variant in h_list] for h, h_list in expanded_hashtags])
    col_names = ['original', 'expanded']
    expanded_hashtag_df = pd.DataFrame(expanded_hashtags, columns=col_names)
    ## save to file
    expanded_hashtag_df.to_csv(out_file_name, sep=',', index=False)

if __name__ == '__main__':
    main()
