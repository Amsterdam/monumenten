#!/bin/sh

set -e
set -u

DIR="$(dirname $0)"

dc() {
	docker-compose -p monumenten -f ${DIR}/docker-compose.yml $*
}

trap 'dc kill ; dc rm -f' EXIT

rm -rf ${DIR}/backups
mkdir -p ${DIR}/backups


dc build

dc up -d database
sleep 50

dc exec -T database update-table.sh bag bag_pand public monumenten
dc exec -T database update-table.sh bag bag_nummeraanduiding public monumenten

dc run --rm importer
dc run --rm db-backup
