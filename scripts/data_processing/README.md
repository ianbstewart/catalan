# Data processing

The scripts in this directory are used to mine, clean and process the data prior to analysis.
This is the order in which the scripts should be run.

## Step by step
0. Store all your archive Twitter files in a single directory, labelled by date in the format "tweets-Month-Day-Year-Hour-Minute-Second.gz"
1. Collect a list of hashtags to mine by browsing Twitter for referendum content,
or by running `bash ht_scrape.sh` and examining the output of common Spanish hashtags. 
Store the list under `~/data/expanded_hashtags.csv`.
This file should have at least two columns for "hashtag" and "sentiment" (pro/anti/neutral).
2. Expand this list of hashtags by generating the lowercased and accent-stripped version of all hashtags: 
`python fix_expanded_hashtags.py`.
This will produce a list of fixed hashtags in `~/data/expanded_fixed_hashtags.csv`.
3. Mine the hashtags from archive: 
`bash mine_hashtags_in_chunks.sh`.
This will generate a multiple chunk files that need to be combined with `bash combine_chunk_files.sh`.
This will produce a single tweet file: `~/data/tweets/archive_Jan-01-17_Oct-31-17_ref_hashtags.json`.
4. The tweets need to be filtered for spam bots and retweets, which is done with: `python filter_tweets_for_spam.py`.
This will produce a filtered tweet file: `~/archive_Jan-01-17_Oct-31-17_ref_hashtags_filtered.json`.
5. Tag all tweets for language using `langid`: `python lang_id_filtered_tweets.py`.
6. Extract all relevant users from the filtered tweets: `python extract_user_groups.py`.
7. We need control tweets for all users in the filtered tweets to compare their non-referendum Catalan use.
We extract all control tweets: `bash mine_extra_user_tweets.sh`.
Then, combine all the control tweets: `bash combine_user_tweets.sh`.
8. Extract relevant data from all user control tweets for later analysis: `python extract_relevant_info_from_extra_user_tweets.py`.
9. Filter relevant data to include only valid control tweets: `python filter_control_tweets.py`
10. Get hashtag counts to report pro/neutral/anti counts for descriptive statistics: `count_hashtags_in_corpus.ipynb`