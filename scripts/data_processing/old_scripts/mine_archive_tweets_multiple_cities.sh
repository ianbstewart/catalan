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
    #echo $CURR_DATE
    RELEVANT_FILES=$(ls $DATA_DIR/tweets-"$CURR_DATE"-[0-9][0-9]-[0-9][0-9].gz)
    ALL_FILES+=($RELEVANT_FILES)
done

## mine files
CITY_FILE=../../data/geo_files/catalonia_municipalities.txt
#CITIES=$(cat $CITY_FILE)
readarray -t CITIES < $CITY_FILE
# grep for all cities at once??
function join_by { local IFS="$1"; shift; echo "$*"; }
CITY_STR_COMBINED=$(join_by "|" "${CITIES[@]}")
# make combined output file
OUT_FILE=../../data/tweets/archive_"$START_STR"_"$END_STR"_catalonia_tweets.json
# mine one file at a time because that's a good idea
for F in "${ALL_FILES[@]}";
do
    echo "mining $F"
    zgrep -E "\"name\":\"($CITY_STR_COMBINED)\"" $F >> $OUT_FILE
done
# for CITY in "${CITIES[@]}";
# do
#     CITY_STR=${CITY/ /_/}
#     OUT_FILE=../../data/tweets/archive_"$START_STR"_"$END_STR"_"$CITY_STR"_tweets.json
#     echo "mining $CITY"
# done