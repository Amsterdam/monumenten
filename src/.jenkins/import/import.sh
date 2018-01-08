#!/bin/sh

set -e
set -u

DIR="$(dirname $0)"

dc() {
	docker-compose -p monumenten -f ${DIR}/docker-compose.yml $*
}

#trap 'dc kill ; dc rm -f' EXIT

rm -rf ${DIR}/backups
mkdir -p ${DIR}/backups

echo "Building dockers"
dc down
dc pull
dc build

dc up -d database
dc up -d elasticsearch
dc run importer /app/.jenkins/docker-wait.sh

dc exec -T database update-table.sh bag bag_pand public monumenten
dc exec -T database update-table.sh bag bag_nummeraanduiding public monumenten

dc run --rm importer

echo "Running backups"
dc exec -T database backup-db.sh monumenten
dc exec -T elasticsearch backup-indices.sh monumenten monumenten

echo "Done"
