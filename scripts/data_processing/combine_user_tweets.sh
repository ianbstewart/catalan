# combine chunked user tweet files
## organize
DATA_DIR=../../data/tweets/extra_user_tweets
DATA_FILES=$(ls $DATA_DIR/*chunk.json)
OUT_FILE=$DATA_DIR/Jan-01-17_Oct-31-17_user_tweets.json
if [ -e $OUT_FILE ];
then
    rm $OUT_FILE
fi
## copy
for F in $DATA_FILES;
do
    echo "copying file $F"
    cat $F >> $OUT_FILE
done
