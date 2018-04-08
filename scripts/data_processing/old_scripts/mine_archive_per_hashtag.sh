## collect files
START_STR=Sep-30-16
END_STR=Oct-31-17
DATE_FMT='+%b-%d-%y'
START_DATE=$(date -d $START_STR $DATE_FMT 2>/dev/null)
END_DATE=$(date -d $END_STR $DATE_FMT 2>/dev/null)
echo $START_DATE
echo $END_DATE
DAY_COUNT=$(( ($(date --date="$END_DATE" +%s) - $(date --date="$START_DATE" +%s)) / (60*60*24) ))

DATA_DIR=/hg190/corpora/twitter-crawl/new-archive
declare -a ALL_FILES

for i in $(seq 1 1 "$DAY_COUNT");
do
    DATE_STR="$START_DATE"+"$i"days
    CURR_DATE=$(date -d $DATE_STR "$DATE_FMT")
    RELEVANT_FILES=$(ls $DATA_DIR/tweets-"$CURR_DATE"-[0-9][0-9]-[0-9][0-9].gz)
    ALL_FILES+=($RELEVANT_FILES)
done

OUT_FILE=../../data/tweets/archive_"$START_STR"_"$END_STR"_"$HASHTAG"_tweets.json
for F in "${ALL_FILES[@]}";
do
    echo "mining $F"
    zgrep -i "\#$HASHTAG" $F >> $OUT_FILE
done
