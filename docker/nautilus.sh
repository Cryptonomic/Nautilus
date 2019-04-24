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

Usage: bash $CMD [OPTIONS] -p [/PATH/TO/CONFIG_FOLDER]]
            [-h] [-v]

Options:
    -a, --all                      builds, links, and starts tezos, postgres, and conseil docker
                                   containers and their respective volumes
    -b, --custom-build-path        specify a custom working directory to use for the build instance, defaults to
                                   $HOME/nautilus/current-date-time
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
    bash $CMD -a -p /$HOME/production-environment-1
                                   # build, initialize, and run docker containers
                                   # for conseil, postgres, and tezos
                                   # takes config files from production-environment-1 folder


EOF
}

# parse command line arguments
SHORT_OPTS='ab:cdhp:tv'
LONG_OPTS='all,custom-build-path:,conseil,database,help,path-to-config:,tezos,volume'
ARGS=$(getopt -o $SHORT_OPTS -l $LONG_OPTS -n "$CMD" -- "$@" 2>/dev/null)
#check getopt command failure
(( $? != 0 )) && fatal "invalid options"
eval set -- "${ARGS}"
# set execution flags and/or execute functions for each option
while true ; do
    case "$1" in
        -a|--all) CONSEIL=1 ; POSTGRES=1 ; TEZOS=1 ; ARRONAX=1 ; shift ;;
        -b|--custom-build-path) build_name="$2" ; shift 2 ;;
	    -c|--conseil) CONSEIL=1 ; shift ;;
        -d|--database) POSTGRES=1 ; shift ;;
        -h|--help) display_usage && exit 0 ; shift ;;
        -p|--path-to-config) path_to_config="$2" ; shift 2 ;;
        -r|--arronax) ARRONAX=1 ; shift ;;
        -t|--tezos) TEZOS=1 ; shift ;;
        -v|--volume) VOLUME=1 ; shift ;;
        --) shift ; break ;;
    esac
done

# ensure necessary command line parameters were specified(man test to see usages, checks contents of a string)
[[ -z "${ARRONAX}${CONSEIL}${POSTGRES}${TEZOS}${VOLUME}" ]] && display_usage \
    && fatal "Please specify at least one container type (examples: -a,-c,-d,-t)."


build_time=$(date "+%Y.%m.%d-%H.%M.%S")
#sets current directory to variable DIR
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
#config file path, should contain exact files and directory structure as that of config/local
PATH_TO_CONFIG="${path_to_config:-$DIR/config/local}"

#working directory

BUILD_NAME="${build_name:-$HOME/nautilus}"
[[ -d "$BUILD_NAME" ]] || mkdir "$BUILD_NAME"
WORKING_DIR="$BUILD_NAME"/"$build_time"
#example: production-environment-1, will default to base folder name of config files
DEPLOYMENT_ENV="$(basename "$PATH_TO_CONFIG")"

#make working directory
[[ -d "$WORKING_DIR" ]] || mkdir "$WORKING_DIR"
(( $? == 0 )) || fatal "Unable to create working directory."


docker network create nautilus
. "$DIR"/app/conseil/build_conseil.sh
. "$DIR"/app/postgres/build_postgres.sh
. "$DIR"/app/tezos/build_tezos.sh
. "$DIR"/app/arronax/build_arronax.sh


remove_postgres_all () {
    docker container stop postgres-"$DEPLOYMENT_ENV"
	docker container rm postgres-"$DEPLOYMENT_ENV"
    docker volume rm pgdata-"$DEPLOYMENT_ENV"
    VOLUME_DIR=$HOME/volumes/pgdata-"$DEPLOYMENT_ENV"
    rm -rf "$VOLUME_DIR"
}


#if conseil flag set build conseil container
[[ "$ARRONAX" ]] && build_arronax "$DEPLOYMENT_ENV" "$WORKING_DIR" "$PATH_TO_CONFIG" "$build_time"

#if conseil flag set build conseil container
[[ "$CONSEIL" ]] && build_conseil "$DEPLOYMENT_ENV" "$WORKING_DIR" "$PATH_TO_CONFIG" "$build_time"

#if postgres flag set build postgres container
[[ "$POSTGRES" ]] && build_postgres "$DEPLOYMENT_ENV" "$WORKING_DIR" "$PATH_TO_CONFIG" "$build_time"

#if tezos flag set build tezos container
[[ "$TEZOS" ]] && build_tezos "$DEPLOYMENT_ENV" "$WORKING_DIR" "$PATH_TO_CONFIG" "$build_time"

#if postgres-volume flag remove postgres volumes
[[ "$VOLUME" ]] && remove_postgres_all

#tezos network protocol flag set check
#[[ $tezosprotocol ]] && set_protocol

exit 0
