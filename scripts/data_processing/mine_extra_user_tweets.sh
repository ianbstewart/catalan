# mine all tweets in archive that were written by specified user
source generate_dates.sh

function mine_archive_files {
    ARCHIVE_FILES=$1
    OUT_FILE=$2
    QUERY_STR=$3
    for ARCHIVE_FILE in $ARCHIVE_FILES; do
	echo "mining $ARCHIVE_FILE"
	zgrep -P "$QUERY_STR" $ARCHIVE_FILE >> $OUT_FILE
    done
}

DATA_DIR=../../data
USER_COUNT_FILE=$DATA_DIR/user_groups.csv
USER_NAMES=$(tail -n+2 $USER_COUNT_FILE | cut -d, -f 2)

# join names
function join_by { local IFS="$1"; shift; echo "$*"; }
USER_NAME_STR=$(join_by "|" $USER_NAMES)
QUERY_STR="\"screen_name\":\"($USER_NAME_STR)\""
CORPUS_DIR=/hg190/corpora/twitter-crawl/new-archive
START_STR=Dec-31-16
END_STR=Oct-31-17
#START_DATE=Dec-31-16
#END_DATE=Oct-31-17

## mine all files at once
#ARCHIVE_FILES=$(generate_date_files "$START_DATE" "$END_DATE")
#OUT_FILE=$DATA_DIR/tweets/extra_user_tweets/"$START_DATE"_"$END_DATE"_user_tweets.json
#if [ -e $OUT_FILE ];
#then
#    rm $OUT_FILE
#fi

## mine one file at a time
# use zgrep because it's FASTER than jq
# one file at a time = TOO SLOW
# need chunks
# for F in $ARCHIVE_FILES;
# do
#     echo "mining file $F"
#     zgrep -P "$QUERY_STR" $ARCHIVE_FILE >> $OUT_FILE
# done

## mine chunks
DATE_FMT='+%b-%d-%y'
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

    OUT_FILE=$DATA_DIR/tweets/extra_user_tweets/"$CURR_START"_"$CURR_END".json
    if [ -e $OUT_FILE ]; then
	rm $OUT_FILE
    fi
    (mine_archive_files "${ARCHIVE_FILES[@]}" $OUT_FILE $QUERY_STR)&    
done