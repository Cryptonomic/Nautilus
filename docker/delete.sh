#!/bin/bash
#
# Master script to build, connect, and run docker containers for tezos, postgres, and conseil on one node/droplet.

#build time
build_time=$(date "+%Y.%m.%d-%H.%M.%S")
CMD="$(basename $0)"

error () { echo "error: $@" >&2; }
fatal () { echo "fatal: $@" >&2; exit 1; }

display_usage () {
    cat <<EOF
Connects to a remote imaging pi, flashes Raspberry CM3 devices with a
Kelvin base image, and partitions SD cards for use in a Kelvin AIRTU.

Connections to the imaging pi are made using SSH.  The --imager-hostname
parameter can be an IP address, but will usually be the hostname of the imager
pi.  SSH connection configuration can be found/specified in "~/.ssh/config".

It is required that CM3 devices are plugged into CMIO boards which are
connected to the imaging pi via USB.  Similarly, it is required that SD cards
are also plugged into the imaging pi via USB using SD card readers.

This script was written to be executed from Jenkins.  When executing from
Jenkins, be sure to create a "jenkins" user on the remote imaging pi and
add the jenkins user public key as an authorized key.

Usage: $CMD -n IMAGER_HOSTNAME -p PROJECT_DIR [-i [/PATH/TO/]IMAGE_FILE]
            [-h] [-v]

Options:
    -h, --help                     display this help and exit
    -i, --image=VALUE              absolute path of gzipped or uncompressed
                                   image file to use for device flashing or
                                   relative image file path from images
                                   directory on imager (see "flashcm3s" script
                                   for more details).  If not specified, the
                                   latest base image is used.
    -n, --imager-hostname=VALUE    hostname of imager (usually found/specified
                                   in ~/.ssh/config)
    -p, --project-dir=VALUE              absolute path to directory containing
                                   project resources such as the Bridge Imaging
                                   repo and AIRTU Hardware Testing repo
    -v, --verbose                  debug mode

Examples:
    $CMD -i sf-imager -p /var/lib/jenkins/projects/flash-devices
                                   # initialize bridge memory connected to
                                   # "sf-imager" device and use directory
                                   # "/var/lib/jenkins/projects/flash-devices"
                                   # for local Git repos and other resources
                                   # required for flashing and partitioning

Report bugs to <leon.barovic@kelvininc.com>.
EOF
}

# parse command line arguments
SHORT_OPTS='cd:hi:n:p:v'
LONG_OPTS='conseil,deployment-environment:,help,image:,imager-hostname:,project-dir:,verbose'
ARGS=$(getopt -o $SHORT_OPTS -l $LONG_OPTS -n "$CMD" -- "$@" 2>/dev/null)
(( $? != 0 )) && fatal "invalid options"
eval set -- "$ARGS"

# set execution flags and/or execute functions for each option
#while true is infinite loop which exits if it hits a break command, break is hit when there's no more things to parse
while true ; do #boilerplate
    case "$1" in #boilerplate #starts at beginning of string and keeps shifting over to pick up parameters
        -h|--help) display_usage && exit 0 ; shift ;; #keep boilerplate
        -i|--image) IMAGE="$2" ; shift 2 ;; #shift command takes everything that's in $2 puts it in $1, $3 into $2, keeps shifting, shift 2 moves it twice, if $2 it gets thrown away, because once you get past $1 you can't access it

        -n|--imager-hostname) IMAGER_HOSTNAME="$2" ; shift 2 ;;
        -p|--path-to-config) PATH_TO_CONFIG="$2" ; shift 2 ;;
        -v|--verbose) VERBOSE=1 ; shift ;;
        -c|--conseil) CONSEIL=1 ; shift ;;
        -d|--deployment-environment) DEPLOYMENT_ENV="$2" ; shift 2;; #CAPS Because it's (was previously)export, if using as const then capitalize
        --) shift ; break ;;
    esac
done


build_conseil () {
	docker container stop conseil-$DEPLOYMENT_ENV
	docker container rm conseil-$DEPLOYMENT_ENV
	cd ./app/conseil
#only time to use . ./script.sh is if you want to affect your currently running shell, it's for setting env
	bash ./build.sh -d "$DEPLOYMENT_ENV" -p "$PATH_TO_CONFIG" "$WORK_DIR"
#       . ./build.sh previously used, initial "." is an alias for the command source
	cd ../..
	docker run --name=conseil-$DEPLOYMENT_ENV --network=nautilus -d -p 1337:1337 conseil-$DEPLOYMENT_ENV
}


#if conseil flag set build conseil container
[[ $CONSEIL ]] && conseil





#each build.sh will need to have, unless user specifies nonlocal path to config files, script will use local
export DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
export PATH_TO_CONFIG="${2:-$DIR/config/local}"
export DEPLOYMENT_ENV="$(basename $PATH_TO_CONFIG)"



docker container rm postgres-$1
docker container rm tezos-node-$1
docker container rm conseil-$1
docker container rm arronax-$1

docker volume rm pgdata-$1
docker volume rm tznode_data-$1
docker volume rm tzclient_data-$1

cd ./app/conseil
. ./build.sh #"$DEPLOYMENT_ENV" "$PATH_TO_CONFIG" "$WORK_DIR"
cd ../..

cd ./app/tezos
. ./build.sh #"$DEPLOYMENT_ENV" "$PATH_TO_CONFIG" "$WORK_DIR"
cd ../..

cd ./app/postgres
. ./build.sh #"$DEPLOYMENT_ENV" "$PATH_TO_CONFIG" "$WORK_DIR"
cd ../..

docker network create nautilus
#volumes have to be constant and as such cannot be included in the build directory
mkdir /PATH_TO_CONFIG/volumes
mkdir /PATH_TO_CONFIG/volumes/pgdata-$DEPLOYMENT_ENV
mkdir /PATH_TO_CONFIG/volumes/tznode_data-$DEPLOYMENT_ENV
mkdir /PATH_TO_CONFIG/volumes/tzclient_data-$DEPLOYMENT_ENV
docker volume create --driver local --opt type=none --opt o=bind --opt device=/$PATH_TO_CONFIG/volumes/pgdata-$DEPLOYMENT_ENV pgdata-$DEPLOYMENT_ENV
docker volume create --driver local --opt type=none --opt o=bind --opt device=/$PATH_TO_CONFIG/volumes/tznode_data-$DEPLOYMENT_ENV tznode_data-$DEPLOYMENT_ENV
docker volume create --driver local --opt type=none --opt o=bind --opt device=/$PATH_TO_CONFIG/volumes/tzclient_data-$DEPLOYMENT_ENV tzclient_data-$DEPLOYMENT_ENV


docker run --name=postgres-$DEPLOYMENT_ENV --network=nautilus -v pgdata-$DEPLOYMENT_ENV:/var/lib/postgresql/data -d -p 5432:5432 postgres-$DEPLOYMENT_ENV
docker run --name=tezos-node-$DEPLOYMENT_ENV --network=nautilus -v tznode_data:/var/run/tezos/node-$DEPLOYMENT_ENV -v tzclient_data:/var/run/tezos/client-$1 -d -p 8732:8732 -p 9732:9732 tezos-node-$DEPLOYMENT_ENV
docker run --name=conseil-$DEPLOYMENT_ENV --network=nautilus -d -p 1337:1337 conseil-$DEPLOYMENT_ENV


yes | docker system prune
