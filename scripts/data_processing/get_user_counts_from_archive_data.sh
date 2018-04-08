source generate_dates.sh
DATA_DIR=/hg190/corpora/twitter-crawl/new-archive
START_DATE=Dec-31-16
END_DATE=Oct-31-17
ARCHIVE_FILES=$(generate_date_files $START_DATE $END_DATE)
#echo "${ARCHIVE_FILES[@]}"
#ARCHIVE_FILES=($DATA_DIR/tweets-Jan-01-17-03-54.gz)
#echo $ARCHIVE_FILES
#python get_user_counts_from_archive_data.py $ARCHIVE_FILES

# do with jq because SO MUCH FASTER OMG
QUERY_STR="fromjson? | .user.screen_name"
OUT_DIR=../../data/tweets/user_counts
if [ ! -e $OUT_DIR ]; then
    mkdir $OUT_DIR
fi
CTR=0
for F in $ARCHIVE_FILES;
do
    OUT_FILE=$OUT_DIR/user_counts_"$CTR".tsv
    echo "mining $F"
    zcat $F | ./jq-linux64 "$QUERY_STR" --raw-input | sort | uniq -c > $OUT_FILE
    CTR=$((CTR + 1))
done