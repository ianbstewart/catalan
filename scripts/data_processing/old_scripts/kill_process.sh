# kill process by name
PROCESS=zgrep
#PROCESS=gzip
#PROCESS="bash mine_hashtags_in_chunks.sh"
#PROCESS="./jq-linux64"
PROCESSES=$(ps aux | grep "$PROCESS" | awk '{print $2}')
echo $PROCESSES
kill $PROCESSES
