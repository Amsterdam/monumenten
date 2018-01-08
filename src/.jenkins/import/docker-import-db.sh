#!/usr/bin/env bash

set -u   # crash on missing environment variables
set -e   # stop on any error
set -x   # log every command.

source /.jenkins/docker-wait.sh

# load data in database
python manage.py migrate
python manage.py run_import
python manage_gevent.py run_add_missing_pand
python manage.py run_bag_key_conversions
python manage.py run_import_validation
python manage.py run_refresh_materialized_views
