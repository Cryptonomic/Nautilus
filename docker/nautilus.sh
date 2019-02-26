#!/bin/bash
#
# Master script to build and run conseil, postgres, and tezos containers and their respective volumes.


# global constants
CMD="$(basename $0)"

# utility functions used by this script
error () { echo "error: $@" >&2; }
fatal () { echo "fatal: $@" >&2; exit 1; }
display_usage () {
    cat <<EOF


Connections to the imaging pi/instance/droplet are made using SSH.  Docker has to be preinstalled and ports 1337, 5432,
8732, 9732, and 19732 will be opened.

This script was written to be executed from Jenkins, but can also be run locally.
If executing from Jenkins, be sure to create a "jenkins" user on the remote imaging pi/instance/droplet and
add the jenkins user public key as an authorized key.
If executing locally, be sure to change the postgres username and password in conseil.conf located in
docker/config/local/conseil/ and use the same username and password in dockerfile for postgres.

Usage: $CMD [OPTIONS] -p [/PATH/TO/CONFIG_FOLDER]]
            [-h] [-v]

Options:
    -a, --all                      builds, links, and starts tezos, postgres, and conseil docker
                                   containers and their respective volumes
    -b, --build-name               creates a working directory within home to use for the build instance, defaults to
                                   nautilus_build_current-date-time
    -c, --conseil                  stops and removes existing conseil container if it exists
                                   and rebuilds and starts a new instance of the conseil container
    -d, --database                 stops and removes existing postgres database container if it exists
                                   and rebuilds only the postgres container
    -h, --help                     display this help and exit
    -n, --protocol                 tezos network("mainnet", "zeronet", "alphanet") if not specified defaults to alphanet
    -p, --path_to_config           absolute path to configuration folder, folder should contain at the very least a conseil folder,
                                   if using a modified schema, a postgres folder with a conseil.sql file. if not specified,
                                   uses configuration files for conseil, postgres and tezos from the config folder in repo.
                                   config folder name will also be used in docker container nomenclature(e.g. config folder name is
                                   prod1, docker container name will be conseil-prod1, postgres-prod1, etc.),default config folder is
                                   "local", it resides within config folder in repo
                                   NOTE: docker volumes will be created here to create persistence
    -t, --tezos                    stops and removes existing tezos container if it exists
                                   and rebuilds and starts the tezos container
    -v, --volume                   REMOVES postgres volume and postgres volume folder, use at own risk as this will
                                   require all blocks to be replaced in the postgres database, this is necessary if
                                   there has been a schema change as simply rebuilding the container will not replace the schema

Examples:
    $CMD -a -p /$HOME/production-environment-1
                                   # build, initialize, and run docker containers
                                   # for conseil, postgres, and tezos
                                   # takes config files from production-environment-1 folder


Report bugs to <swap@cryptonomic.tech>.
EOF
}

# parse command line arguments
SHORT_OPTS='ab:cdh:p:tv'
LONG_OPTS='all,build-name:,conseil,database,help,path-to-config:,tezos,volume'
ARGS=$(getopt -o $SHORT_OPTS -l $LONG_OPTS -n "$CMD" -- "$@" 2>/dev/null)
#check getopt command failure
(( $? != 0 )) && fatal "invalid options"
eval set -- "${ARGS}"
# set execution flags and/or execute functions for each option
while true ; do
    case "$1" in
        -a|--all) CONSEIL=1 ; POSTGRES=1 ; TEZOS=1 ; shift ;;
        -b|--build-name) build_name="$2" ; shift 2 ;;
	    -c|--conseil) CONSEIL=1 ; shift ;;
        -d|--database) POSTGRES=1 ; shift ;;
        -h|--help) display_usage && exit 0 ; shift ;;
        -p|--path-to-config) path_to_config="$2" ; shift 2 ;;
        -t|--tezos) TEZOS=1 ; shift ;;
        -v|--volume) VOLUME=1 ; shift ;;
        --) shift ; break ;;
    esac
done

# ensure necessary command line parameters were specified(man test to see usages, checks contents of a string)
[[ -z "${CONSEIL}${POSTGRES}${TEZOS}${VOLUME}" ]] && display_usage \
    && fatal "Please specify at least one container type (examples: -a,-c,-d,-t)."


build_time=$(date "+%Y.%m.%d-%H:%M")
#sets current directory to variable DIR
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
#config file path, should contain exact files and directory structure as that of config/local
PATH_TO_CONFIG="${path_to_config:-$DIR/config/local}"

#working directory
BUILD_NAME="${build_name:-nautilus_build_"$build_time"}"
WORKING_DIR=$HOME/"$BUILD_NAME"
#example: production-environment-1, will default to base folder name of config files
DEPLOYMENT_ENV="$(basename "$PATH_TO_CONFIG")"
#make working directory
[[ -d "$WORKING_DIR" ]] || mkdir "$WORKING_DIR"
#create variable for tezos-network(alphanet or mainnet)
tezosnetwork=`cat "$PATH_TO_CONFIG"/tezos/tezos_network.txt`

docker network create nautilus

build_conseil () { 
	docker container stop conseil-"$DEPLOYMENT_ENV"
	docker container rm conseil-"$DEPLOYMENT_ENV"

	CONSEIL_WORK_DIR="$WORKING_DIR"/conseil-"$DEPLOYMENT_ENV"
    mkdir "$CONSEIL_WORK_DIR"
    cd "$CONSEIL_WORK_DIR"

    . "$DIR"/app/conseil/build.sh

    cp "$PATH_TO_CONFIG"/conseil/conseil.conf ./conseil.conf
    conseil_conf_file=./conseil.conf
    {
    read line1
    read line2
    read line3
    } < "$PATH_TO_CONFIG"/conseil/credentials.txt
    line1=`echo $line1`
    line2=`echo $line2`
    line3=`echo $line3`

    sed -i "s/databaseName=.*/$line1/g" "$conseil_conf_file"
    sed -i "s/user=.*/$line2/g" "$conseil_conf_file"
    sed -i "s/password=.*/$line3/g" "$conseil_conf_file"

    cp "$PATH_TO_CONFIG"/conseil/runconseil-lorre.sh ./build/
    cp ./conseil.conf ./build/


    cp ./Conseil/src/main/resources/logback.xml ./build/
    #cp "$PATH_TO_CONFIG"/conseil/runconseil-lorre.sh ./build/


    docker build -f "$DIR"/app/conseil/dockerfile -t conseil-"$DEPLOYMENT_ENV" .
    rm ./build
   	docker run --name=conseil-"$DEPLOYMENT_ENV" --network=nautilus -d -p 1337:1337 conseil-"$DEPLOYMENT_ENV"

	yes | docker system prune
}

build_postgres () {
    #declaring persistent volumes
    #current volume created check
    [[ -d $HOME/volumes ]] || mkdir $HOME/volumes
    [[ -d $HOME/volumes/pgdata-"$DEPLOYMENT_ENV" ]] || mkdir $HOME/volumes/pgdata-"$DEPLOYMENT_ENV"

    docker volume create --driver local --opt type=none --opt o=bind --opt device=$HOME/volumes/pgdata-"$DEPLOYMENT_ENV" pgdata-"$DEPLOYMENT_ENV"

    docker container stop postgres-"$DEPLOYMENT_ENV"
	docker container rm postgres-"$DEPLOYMENT_ENV"

    #check out schema and put it in the right place


    POSTGRES_WORK_DIR="$WORKING_DIR"/postgres/
    mkdir "$POSTGRES_WORK_DIR"

    cp ./app/postgres/dockerfile "$POSTGRES_WORK_DIR"/dockerfile
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



    #check out schema and put it in the right place
    mv $PATH_TO_CONFIG/postgres/conseil.sql $PATH_TO_CONFIG/postgres/conseil.sql.bak
    wget https://raw.githubusercontent.com/Cryptonomic/Conseil/master/doc/conseil.sql > $PATH_TO_CONFIG/postgres/conseil.sql

    #place schema into working directory for auditability
    ln -s $PATH_TO_CONFIG/postgres/conseil.sql ./conseil.sql
    docker build -f "$POSTGRES_WORK_DIR"/dockerfile -t postgres-"$DEPLOYMENT_ENV" .

	docker run --name=postgres-"$DEPLOYMENT_ENV" --network=nautilus -v pgdata-$DEPLOYMENT_ENV:/var/lib/postgresql/data -d -p 5432:5432 postgres-"$DEPLOYMENT_ENV"
}

build_tezos () {
    #volumes creation for persistent storage
    [[ -d $HOME/volumes ]] || mkdir $HOME/volumes
    [[ -d $HOME/volumes/tznode_data-"$DEPLOYMENT_ENV" ]] || mkdir $HOME/volumes/tznode_data-"$DEPLOYMENT_ENV"
    [[ -d $HOME/volumes/tzclient_data-"$DEPLOYMENT_ENV" ]] || mkdir $HOME/volumes/tzclient_data-"$DEPLOYMENT_ENV"
    #stop and remove current container
    docker container stop tezos-node-"$DEPLOYMENT_ENV"
	docker container rm tezos-node-"$DEPLOYMENT_ENV"

    #createdocker volumes
    docker volume create --driver local --opt type=none --opt o=bind --opt device=$HOME/volumes/tznode_data-"$DEPLOYMENT_ENV" tznode_data-"$DEPLOYMENT_ENV"
    docker volume create --driver local --opt type=none --opt o=bind --opt device=$HOME/volumes/tzclient_data-"$DEPLOYMENT_ENV" tzclient_data-"$DEPLOYMENT_ENV"

	#make tezos subdirectory
    TEZOS_WORK_DIR="$WORKING_DIR"/tezos
    mkdir "$TEZOS_WORK_DIR"

    #copy dockerfile from nautilus
    cp ./app/tezos/dockerfile "$TEZOS_WORK_DIR"/dockerfile

    #replace tezos network in dockerfile
    tz_dockerfile="$TEZOS_WORK_DIR"/dockerfile
    sed -i "s/protocol/$tezosnetwork/g" "$tz_dockerfile"
    cd "$TEZOS_WORK_DIR"

    #build and run docker container
    docker build -f dockerfile -t tezos-node-"$DEPLOYMENT_ENV" . &&
    docker run --name=tezos-node-"$DEPLOYMENT_ENV" --network=nautilus -v tznode_data:/var/run/tezos/node-"$DEPLOYMENT_ENV" -v tzclient_data:/var/run/tezos/client-"$DEPLOYMENT_ENV" -d -p 8732:8732 -p 9732:9732 tezos-node-"$DEPLOYMENT_ENV"
}

remove_postgres_volumes () {
    docker container stop postgres-"$DEPLOYMENT_ENV"
	docker container rm postgres-"$DEPLOYMENT_ENV"
    docker volume rm pgdata-"$DEPLOYMENT_ENV"
    sudo rm -rf $HOME/volumes/pgdata-"$DEPLOYMENT_ENV"
}

#set_protocol () {
#    if [[ tezosprotocol == "alphanet" || tezosprotocol == "mainnet" || tezosprotocol == "zeronet" ]]; then
#        build_tezos
#    else
#        fatal "Invalid tezos network specified"
#    fi
#}

#if conseil flag set build conseil container
[[ $CONSEIL ]] && build_conseil

#if postgres flag set build postgres container
[[ $POSTGRES ]] && build_postgres

#if tezos flag set build tezos container
[[ "$TEZOS" ]] && build_tezos

#if postgres-volume flag remove postgres volumes
[[ $VOLUME ]] && remove_postgres_volumes

#tezos network protocol flag set check
#[[ $tezosprotocol ]] && set_protocol

exit 0