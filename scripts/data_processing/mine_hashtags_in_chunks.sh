# mine hashtags in file chunks
source generate_dates.sh
function mine_archive_files {
    ARCHIVE_FILES=$1
    OUT_FILE=$2
    QUERY_STR=$3
    for ARCHIVE_FILE in $ARCHIVE_FILES; do
	echo "mining $ARCHIVE_FILE"
	# need to use zgrep because jq takes FOREVER ;_;
	# jq
	#zcat $ARCHIVE_FILE | ./jq-linux64 -c "$QUERY_STR" --raw-input >> $OUT_FILE
	# grep
	zgrep -P "$QUERY_STR" $ARCHIVE_FILE >> $OUT_FILE
    done
}
DATA_DIR=../../data

## load hashtags
# regular list
#HASHTAG_FILE=$DATA_DIR/expanded_hashtags.csv
# expanded list
HASHTAG_FILE=$DATA_DIR/expanded_fixed_hashtags.csv

## split hashtags
# all hashtags
HASHTAG_LIST=( $(tail -n +2 $HASHTAG_FILE | cut -d ',' -f2))
# subset of hashtags for debuggging
#HASHTAG_LIST=( $(tail -n +112 $HASHTAG_FILE | cut -d ',' -f2))
# sanity check: dummy hashtag list
#HASHTAG_LIST=( "lol" )
HASHTAG_COUNT="${#HASHTAG_LIST[@]}"
echo "$HASHTAG_COUNT hashtags collected"

## preprocess hashtags
# jq: add hashtags and quotes
#for ((i=0;i<$HASHTAG_COUNT;i++)); do
#    HASHTAG_LIST[i]="\"#${HASHTAG_LIST[i]}\""
#done
# grep: add hashtags
for ((i=0;i<$HASHTAG_COUNT;i++)); do
   HASHTAG_LIST[i]="#${HASHTAG_LIST[i]}"
done

## define QUERY string
function join_by { local IFS="$1"; shift; echo "$*"; }
# jq
#DELIM=","
# grep
DELIM="|"
HASHTAG_STR=$(join_by $DELIM "${HASHTAG_LIST[@]}")
# jq 
#QUERY_STR="fromjson? | select(.text | contains($HASHTAG_STR))"
# grep
QUERY_STR=$HASHTAG_STR
echo $QUERY_STR

## define dates
function mine_archive_files {
    ARCHIVE_FILES=$1
    OUT_FILE=$2
    QUERY_STR=$3
    for ARCHIVE_FILE in $ARCHIVE_FILES; do
	echo "mining $ARCHIVE_FILE"
	# need to use zgrep because jq takes FOREVER ;_;
	# jq
	#zcat $ARCHIVE_FILE | ./jq-linux64 -c "$QUERY_STR" --raw-input >> $OUT_FILE
	# grep
	zgrep -P "$QUERY_STR" $ARCHIVE_FILE >> $OUT_FILE
    done
}
DATA_DIR=../../data

## load hashtags
# regular list
#HASHTAG_FILE=$DATA_DIR/expanded_hashtags.csv
# expanded list
HASHTAG_FILE=$DATA_DIR/expanded_fixed_hashtags.csv

## split hashtags
# all hashtags
HASHTAG_LIST=( $(tail -n +2 $HASHTAG_FILE | cut -d ',' -f2))
# subset of hashtags for debuggging
#HASHTAG_LIST=( $(tail -n +112 $HASHTAG_FILE | cut -d ',' -f2))
# sanity check: dummy hashtag list
#HASHTAG_LIST=( "lol" )
HASHTAG_COUNT="${#HASHTAG_LIST[@]}"
echo "$HASHTAG_COUNT hashtags collected"

## preprocess hashtags
# jq: add hashtags and quotes
#for ((i=0;i<$HASHTAG_COUNT;i++)); do
#    HASHTAG_LIST[i]="\"#${HASHTAG_LIST[i]}\""
#done
# grep: add hashtags
for ((i=0;i<$HASHTAG_COUNT;i++)); do
   HASHTAG_LIST[i]="#${HASHTAG_LIST[i]}"
done

## define QUERY string
function join_by { local IFS="$1"; shift; echo "$*"; }
# jq
#DELIM=","
# grep
DELIM="|"
HASHTAG_STR=$(join_by $DELIM "${HASHTAG_LIST[@]}")
# jq 
#QUERY_STR="fromjson? | select(.text | contains($HASHTAG_STR))"
# grep
QUERY_STR=$HASHTAG_STR
echo $QUERY_STR

## define dates
DATE_FMT='+%b-%d-%y'
START_STR=Dec-31-16
#START_STR=Mar-31-17
#END_STR=Apr-14-17
#END_STR=Sep-01-17
END_STR=Oct-31-17
START_DATE=$(date -d $START_STR $DATE_FMT 2>/dev/null)
END_DATE=$(date -d $END_STR $DATE_FMT 2>/dev/null)
START_DATE_SEC=$(date -d $START_DATE +%s)
END_DATE_SEC=$(date -d $END_DATE +%s)
DAY_COUNT=$(( ($END_DATE_SEC - $START_DATE_SEC) / (60*60*24) ))
# days per chunk
CHUNK_SIZE=14
# number of chunks
CHUNK_COUNT=$((($DAY_COUNT + $CHUNK_SIZE - 1) / $CHUNK_SIZE))

for i in $(seq 0 1 "$CHUNK_COUNT");
do
    # update current start/end
    N=$(( $i * $CHUNK_SIZE ))
    CURR_START_STR="$START_STR"+"$N"days
    CURR_END_STR="$CURR_START_STR"+"$CHUNK_SIZE"days
    CURR_START=$(date -d $CURR_START_STR $DATE_FMT)
    CURR_END=$(date -d $CURR_END_STR $DATE_FMT)
    CURR_START_SEC=$(date -d $CURR_START +%s)
    CURR_END_SEC=$(date -d $CURR_END +%s)
    if [ $CURR_START_SEC -ge $END_DATE_SEC ]; then
	break
    fi
    if [ $CURR_END_SEC -ge $END_DATE_SEC ]; then
	CURR_END=$END_DATE
    fi
    ARCHIVE_FILES=$(generate_date_files $CURR_START $CURR_END)
    echo "chunk $i"
    # echo "${ARCHIVE_FILES[@]}"

    OUT_FILE=$DATA_DIR/tweets/archive_full_"$CURR_START"_"$CURR_END"_ref_hashtags_chunk.json
    if [ -e $OUT_FILE ]; then
	rm $OUT_FILE
    fi
    (mine_archive_files "${ARCHIVE_FILES[@]}" $OUT_FILE $QUERY_STR)&    
done