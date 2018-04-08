# combine chunked files into single JSON file
DATA_DIR=../../data/tweets
CHUNK_FILES=$(ls $DATA_DIR/*chunk.json)
echo $CHUNK_FILES
START_DATE=Jan-01-17
END_DATE=Oct-31-17
OUT_FILE=$DATA_DIR/archive_"$START_DATE"_"$END_DATE"_ref_hashtags.json
echo "output file $OUT_FILE"
for F in $CHUNK_FILES;
do
    echo "copying file $F"
    cat $F >> $OUT_FILE
done