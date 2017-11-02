#!/usr/bin/env bash

set -u
set -e

# wait for elastic
NEXT_WAIT_TIME=0
until nc -z elasticsearch 9200 || [ $NEXT_WAIT_TIME -eq 10 ]
do
    echo "Waiting for elastic..."
    sleep $(( NEXT_WAIT_TIME++ ))
done

# wait for postgres
while ! nc -z database 5432
do
	echo "Waiting for postgres..."
	sleep 2
done
