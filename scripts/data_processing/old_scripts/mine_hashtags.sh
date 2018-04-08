source generate_dates.sh
DATA_DIR=../../data

## load hashtags
# regular list
#HASHTAG_FILE=$DATA_DIR/expanded_hashtags.csv
# expanded list
HASHTAG_FILE=$DATA_DIR/expanded_fixed_hashtags.csv
HASHTAG_LIST=( $(tail -n +2 $HASHTAG_FILE | cut -d ',' -f2))

# echo "${HASHTAG_LIST[@]}"
HASHTAG_COUNT="${#HASHTAG_LIST[@]}"
echo "$HASHTAG_COUNT hashtags collected"
# add quote marks to all hashtags
for ((i=0;i<$HASHTAG_COUNT;i++)); do
    HASHTAG_LIST[i]="\"#${HASHTAG_LIST[i]}\""
done

## define file(s)
# ARCHIVE_FILE=$DATA_DIR/tweets/archive_Sep-30-16_Oct-31-17_ES_tweets.json
#START_STR=Jan-01-17
START_STR=Aug-31-17
END_STR=Oct-31-17
ARCHIVE_FILES=$(generate_date_files $START_STR $END_STR)
#ARCHIVE_FILES=(/hg190/corpora/twitter-crawl/new-archive/tweets-Oct-01-17-04-06.gz)

## define hashtag string
function join_by { local IFS="$1"; shift; echo "$*"; }
HASHTAG_STR=$(join_by "," "${HASHTAG_LIST[@]}")

## mine!
# basic query
#QUERY_STR="select(.text | contains($HASHTAG_STR)) | [.text, .user.screen_name, .id, .created_at]"
# fromjson? used to check for valid JSON => avoids breaking on badly formatted JSON lines
# some values
#QUERY_STR="fromjson? | select(.text | contains($HASHTAG_STR)) | [.text, .user.screen_name, .id, .created_at]"
# all values
QUERY_STR="fromjson? | select(.text | contains($HASHTAG_STR))"

## single file
# --raw-input and fromjson? used to check for valid JSON
#OUT_FILE=${ARCHIVE_FILE/.json/_ref_hashtags_fixed.json}
#./jq-linux64 -c "$QUERY_STR" --raw-input $ARCHIVE_FILE > $OUT_FILE

## multiple files
OUT_FILE=$DATA_DIR/tweets/archive_full_"$START_STR"_"$END_STR"_ref_hashtags_fixed_tmp.json
if [ -e $OUT_FILE ]; then
    rm $OUT_FILE
fi
for ARCHIVE_FILE in $ARCHIVE_FILES; do
    echo "mining $ARCHIVE_FILE"
    zcat $ARCHIVE_FILE | ./jq-linux64 -c "$QUERY_STR" --raw-input >> $OUT_FILE
done