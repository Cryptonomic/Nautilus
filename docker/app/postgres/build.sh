#!/bin/bash

#check out schema and put it in the right place

cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd
. ../../parse_opt.sh

POSTGRES_WORK_DIR="$HOME/postgres_build_$BUILD_NAME"
mkdir "$POSTGRES_WORK_DIR"

#place schema into working directory for auditability
wget https://raw.githubusercontent.com/Cryptonomic/Conseil/master/doc/conseil.sql > $POSTGRES_WORK_DIR/conseil.sql

wget https://raw.githubusercontent.com/Cryptonomic/Conseil/master/doc/conseil.sql > $PATH_TO_CONFIG/postgres/conseil.sql


ln -s $PATH_TO_CONFIG/postgres/conseil.sql conseil.sql
docker build -f $DIR/docker/app/postgres/dockerfile -t postgres-$DEPLOYMENT_ENV .


