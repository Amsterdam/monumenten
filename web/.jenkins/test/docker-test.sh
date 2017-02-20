#!/usr/bin/env bash

set -u # crash on missing env
set -e # stop on any error

python ../../manage.py test
