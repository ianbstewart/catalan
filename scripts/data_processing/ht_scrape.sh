cat ../../data/tweets/*.json | jq '.entities.hashtags[] | .text' | sort | uniq -c | sort -nr > ../../data/tweets/common_hts_in_5ht_tweets.txt
cat /hg190/istewart6/CSS_replication_project/data/tweets/archive_Sep-30-16_Oct-31-17_ES_tweets.json | jq '.entities.hashtags[] | .text' | sort | uniq -c | sort -nr > ../../data/tweets/common_hts_in_ES_tweets.txt
