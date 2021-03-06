#!/bin/sh

set -e
set -u

DIR="$(dirname $0)"

dc() {
	docker-compose -p monumenten -f ${DIR}/docker-compose.yml $*
}

trap 'dc kill ; dc down ; dc rm -f' EXIT

rm -rf ${DIR}/backups
mkdir -p ${DIR}/backups

echo "Building dockers"
dc down
dc pull
dc build

dc up -d database
dc up -d elasticsearch
dc run importer /.jenkins/docker-wait.sh

dc run --rm importer

echo "Running backups"
dc exec -T database backup-db.sh monumenten
dc exec -T elasticsearch backup-indices.sh monumenten monumenten
dc down -v
echo "Done"
