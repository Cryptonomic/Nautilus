#!/bin/bash

build_tezos () {

    DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

    DEPLOYMENT_ENV="$1"
    WORKING_DIR="$2"
    PATH_TO_CONFIG="$3"
    build_time="$4"

    #volumes creation for persistent storage
    [[ -d $HOME/volumes ]] || mkdir $HOME/volumes

    #stop and remove current container
    current_tezos_container=tezos-node-"$DEPLOYMENT_ENV"
    docker container stop "$current_tezos_container"
	docker container rm "$current_tezos_container"

    #createdocker volumes
    #docker volume create --driver local --opt type=none --opt o=bind --opt device=$HOME/mnt/tezos-"$DEPLOYMENT_ENV" tznode_data-"$DEPLOYMENT_ENV"

    #make tezos subdirectory
    TEZOS_WORK_DIR="$WORKING_DIR"/tezos-node-"$DEPLOYMENT_ENV"
    mkdir "$TEZOS_WORK_DIR"

    #copy dockerfile from nautilus
    cp "$DIR"/dockerfile "$TEZOS_WORK_DIR"/dockerfile


    tezos_network=`cat "$PATH_TO_CONFIG"/tezos/tezos_network.txt`

    cd "$TEZOS_WORK_DIR"

    #replace tezos network in dockerfile
    tz_dockerfile="$TEZOS_WORK_DIR"/dockerfile
    sed -i "s/protocol/$tezos_network/g" "$tz_dockerfile"


    #build and run docker container
    docker build -f "$TEZOS_WORK_DIR"/dockerfile -t tezos-node-"$DEPLOYMENT_ENV" .
    (( $? == 0 )) || fatal "Unable to build tezos container"
    docker run --name=tezos-node-"$DEPLOYMENT_ENV" --network=host -d tezos-node-"$DEPLOYMENT_ENV"
    (( $? == 0 )) || fatal "Unable to run tezos container, please check ports and current configurations"
}
