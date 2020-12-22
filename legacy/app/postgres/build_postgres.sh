#!/bin/bash



build_postgres () {

    DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

    DEPLOYMENT_ENV="$1"
    WORKING_DIR="$2"
    PATH_TO_CONFIG="$3"

    #declaring persistent volumes
    #current volume created check
    VOLUME_DIR=$HOME/volumes/pgdata-"$DEPLOYMENT_ENV"
    [[ -d $HOME/volumes ]] || mkdir $HOME/volumes
    [[ -d $HOME/volumes/pgdata-"$DEPLOYMENT_ENV" ]] || mkdir "$VOLUME_DIR"

    docker volume create --driver local --opt type=none --opt o=bind --opt device=$HOME/volumes/pgdata-"$DEPLOYMENT_ENV" pgdata-"$DEPLOYMENT_ENV"
    current_postgres_container=postgres-"$DEPLOYMENT_ENV"
    docker container stop "$current_postgres_container"
	docker container rm "$current_postgres_container"

    #check out schema and put it in the right place
    POSTGRES_WORK_DIR="$WORKING_DIR"/postgres-"$DEPLOYMENT_ENV"
    mkdir "$POSTGRES_WORK_DIR"
    cp "$DIR"/dockerfile "$POSTGRES_WORK_DIR"/dockerfile
    postgres_dockerfile="$POSTGRES_WORK_DIR"/dockerfile

    #check out schema and place in working directory
    cd "$POSTGRES_WORK_DIR"
    wget https://raw.githubusercontent.com/Cryptonomic/Conseil/master/doc/conseil.sql

    #Set required env vars for Docker
    POSTGRES_ENV_FILE="$PATH_TO_CONFIG/postgres/env.list"
    source ${POSTGRES_ENV_FILE}

    export CONSEILDB_USER
    export CONSEILDB_PASSWORD
    export CONSEILDB_DBNAME

    #build docker container
    docker build --build-arg CONSEILDB_USER=${CONSEILDB_USER} --build-arg CONSEILDB_PASSWORD=${CONSEILDB_PASSWORD} --build-arg CONSEILDB_DBNAME=${CONSEILDB_DBNAME}  -f dockerfile -t postgres-"$DEPLOYMENT_ENV" .
    (( $? == 0 )) || fatal "Unable to build postgres container"
	docker run --name=postgres-"$DEPLOYMENT_ENV" --network=nautilus -v pgdata-"$DEPLOYMENT_ENV":/var/lib/postgresql/data -d -p 5432:5432 postgres-"$DEPLOYMENT_ENV"
    (( $? == 0 )) || fatal "Unable to run postgres container, please check ports 5432 and any running instances of postgres"
}
