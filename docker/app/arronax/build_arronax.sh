#!/bin/bash

build_arronax () {


    DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

    DEPLOYMENT_ENV="$1"
    WORKING_DIR="$2"
    PATH_TO_CONFIG="$3"
    build_time="$4"

    current_container=conseil-"$DEPLOYMENT_ENV"

    docker container stop "$current_container"
    docker container rm "$current_container"
    mkdir /tmp/$WORKING_DIR && cd $WORKING_DIR

    git clone https://github.com/Cryptonomic/Arronax.git
    cd Arronax

    npm install

    cp -f ../../env/$1/config.json ./public

    npm run build

    docker build -f dockerfile -t arronax-$DEPLOYMENT_ENV .
    docker run --name=arronax-$DEPLOYMENT_ENV --network=nautilus -d -p 8080:80 arronax-$DEPLOYMENT_ENV
}