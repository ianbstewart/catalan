# generate all files corresponding
# to dates in range
# assume Month{3}-Day{2}-Year{2} format
# e.g. Jan-22-17
function generate_date_files {
    START_STR=$1
    END_STR=$2
    DATE_FMT='+%b-%d-%y'
    START_DATE=$(date -d $START_STR $DATE_FMT 2>/dev/null)
    END_DATE=$(date -d $END_STR $DATE_FMT 2>/dev/null)

    DAY_COUNT=$(( ($(date --date="$END_DATE" +%s) - $(date --date="$START_DATE" +%s)) / (60*60*24) ))
    
    DATA_DIR=/hg190/corpora/twitter-crawl/new-archive
    declare -a ALL_FILES
    
    for i in $(seq 1 1 "$DAY_COUNT");
    do
	DATE_STR="$START_DATE"+"$i"days
	CURR_DATE=$(date -d $DATE_STR "$DATE_FMT")
	FILE_PATTERN=tweets-"$CURR_DATE"-[0-9][0-9]-[0-9][0-9].gz
	#echo $CURR_DATE
	RELEVANT_FILES=$(ls $DATA_DIR/$FILE_PATTERN)
	ALL_FILES+=($RELEVANT_FILES)
    done
    echo "${ALL_FILES[@]}"
}