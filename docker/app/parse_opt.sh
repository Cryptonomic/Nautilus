#!/bin/bash
# utility functions used by this script
error () { echo "error: $@" >&2; }
fatal () { echo "fatal: $@" >&2; exit 1; }



while true ; do
    case "$1" in
        -a|--all) CONSEIL=1; POSTGRES=1; TEZOS=1 ; shift ;;
        -b|--build-name) build_name="$2" ; shift 2 ;;
	    -c|--conseil) CONSEIL=1 ; shift ;;
        -d|--database) POSTGRES=1 ; shift ;;
        -h|--help) display_usage && exit 0 ; shift ;;
        -n|--protocol) protocol="$2" ; shift 2 ;;
        -p|--path-to-config) path_to_config="$2" ; shift 2 ;;
        -t|--tezos) TEZOS=1 ; shift ;;
        -v|--volume) VOLUME=1 ; shift ;;
        --) shift ; break ;;
    esac
done

# set command line arguments
SHORT_OPTS='ab:cd:hn:p:tv'
LONG_OPTS='all,build-name:,conseil,database,help,:,path-to-config:,protocol:,tezos,volume'

eval set -- "$ARGS"

#parse command line parameters
ARGS=$(getopt -o $SHORT_OPTS -l $LONG_OPTS -n "$CMD" -- "$@" 2>/dev/null)
#check getopt command failure
(( $? != 0 )) && fatal "invalid options"


# test necessary command line parameters were specified
[[ -z "${CONSEIL}${POSTGRES}${TEZOS}" ]] && display_usage \
    && fatal "Please specify at least one container type (examples: -a,-c,-d,-t)."

default_network="alphanet"
build_time=$(date "+%Y.%m.%d-%H.%M.%S")
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PATH_TO_CONFIG="${path_to_config:-$DIR/config/local}"
BUILD_NAME="${build_name:-$build_time}"
DEPLOYMENT_ENV="$(basename $PATH_TO_CONFIG)"
tezosprotocol="${default_network:-$protocol}"
