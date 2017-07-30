#!/bin/bash

LOGFILE="record.log"

# push all output to the log file
exec 1> >( tee -a $LOGFILE ) 2>&1

# log start time
echo Starting at $(date)

# record in hourly chunks
SEC=`expr 60 \* 60`
echo Creating files every $SEC

# start recording
# sox -d bubbles_.wav channels 1 rate 48k trim 0 $SEC : newfile : restart
arecord -v -D plughw:CARD=CODEC,DEV=0 -f dat -t wav -c 1 --max-file-time=$SEC --use-strftime ./wav/%Y-%m-%d-%H-%M-%S.wav

echo Done

