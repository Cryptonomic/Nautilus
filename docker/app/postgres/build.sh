#!/bin/bash

#check out schema and put it in the right place

cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd
. ../parse_opt.sh



POSTGRES_WORK_DIR="$HOME/postgres_build_$BUILD_NAME"
mkdir "$POSTGRES_WORK_DIR"

cp ./dockerfile "$POSTGRES_WORK_DIR"/dockerfile

#copy username and password from conseil.conf to postgres dockerfile
username=$(grep "user" "$PATH_TO_CONFIG"/conseil/conseil.conf ; shift 6 ;)
sed 's/databaseusername/username/g' dockerfile
$password=$(grep "password" "$PATH_TO_CONFIG"/conseil/conseil.conf ; shift 8 ;)



#place schema into working directory for auditability
wget https://raw.githubusercontent.com/Cryptonomic/Conseil/master/doc/conseil.sql > $POSTGRES_WORK_DIR/conseil.sql

wget https://raw.githubusercontent.com/Cryptonomic/Conseil/master/doc/conseil.sql > $PATH_TO_CONFIG/postgres/conseil.sql


ln -s $PATH_TO_CONFIG/postgres/conseil.sql conseil.sql
docker build -f "$POSTGRES_WORK_DIR"/dockerfile -t postgres-"$DEPLOYMENT_ENV" .


