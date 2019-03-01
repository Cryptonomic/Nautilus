#!/bin/bash



build_postgres () {

    DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

    DEPLOYMENT_ENV="$1"
    WORKING_DIR="$2"
    PATH_TO_CONFIG="$3"
    build_time="$4"
    #declaring persistent volumes
    #current volume created check
    [[ -d $HOME/volumes ]] || mkdir $HOME/volumes
    [[ -d $HOME/volumes/pgdata-"$DEPLOYMENT_ENV" ]] || mkdir $HOME/volumes/pgdata-"$DEPLOYMENT_ENV"

    docker volume create --driver local --opt type=none --opt o=bind --opt device=$HOME/volumes/pgdata-"$DEPLOYMENT_ENV" pgdata-"$DEPLOYMENT_ENV"
    current_postgres_container=postgres-"$DEPLOYMENT_ENV"
    docker container stop "$current_postgres_container"
	docker container rm "$current_postgres_container"

    #check out schema and put it in the right place


    POSTGRES_WORK_DIR="$WORKING_DIR"/postgres-"$DEPLOYMENT_ENV"
    mkdir "$POSTGRES_WORK_DIR"

    cp "$DIR"/dockerfile "$POSTGRES_WORK_DIR"/dockerfile
    postgres_dockerfile="$POSTGRES_WORK_DIR"/dockerfile
    #change postgres databasename, username, and password
    {
    read line1
    read line2
    read line3
    } < "$PATH_TO_CONFIG"/postgres/credentials.txt
    line1=`echo $line1`
    line2=`echo $line2`
    line3=`echo $line3`

    sed -i "s/ENV POSTGRES_USER=.*/$line1/g" "$postgres_dockerfile"
    sed -i "s/ENV POSTGRES_PASSWORD=.*/$line2/g" "$postgres_dockerfile"
    sed -i "s/ENV POSTGRES_DB=.*/$line3/g" "$postgres_dockerfile"



    #check out schema and place in working directory
    cd "$POSTGRES_WORK_DIR"
    wget https://raw.githubusercontent.com/Cryptonomic/Conseil/master/doc/conseil.sql

    #build docker container
    docker build -f dockerfile -t postgres-"$DEPLOYMENT_ENV" .
    (( $? == 0 )) || fatal "Unable to build postgres container"
	docker run --name=postgres-"$DEPLOYMENT_ENV" --network=nautilus -v pgdata-"$DEPLOYMENT_ENV":/var/lib/postgresql/data -d -p 5432:5432 postgres-"$DEPLOYMENT_ENV"

}
