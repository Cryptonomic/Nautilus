#!/bin/bash

cd util

mkdir tezos-nodes

cd tezos-nodes

mkdir data

cd data

mkdir "$4"

cd "$4"

if [ "$1" == "mainnet" ]; then
    if [ "$5" == "full" -o "$5" == "archive" ]; then
        wget https://snaps.tulip.tools/mainnet_2020-07-13_16:00.full -O img
    fi
    if [ "$5" == "experimental-rolling" ]; then
        wget https://snaps.tulip.tools/mainnet_2020-07-13_16:00.rolling -O img
    fi
else
    if [ "$5" == "full" -o "$5" == "archive" ]; then
        wget https://snaps.tulip.tools/carthagenet_2020-07-13_16:00.full -O img
    fi
    if [ "$5" == "experimental-rolling" ]; then
        wget https://snaps.tulip.tools/carthagenet_2020-07-13_16:00.rolling -O img
    fi
fi

#docker run --rm -v "$PWD:/var/run/tezos/node/data" -v "$PWD:/config" "tezos/tezos:latest-release" tezos-config --network "$1" --cors-header='content-type' --cors-origin='*' --rpc-addr 127.0.0.1:"$2" --net-addr 127.0.0.1:"$3" --history-mode "$5" --config-file "/config/config.json" init

docker run --rm -v "$PWD:/var/run/tezos/" -v "$PWD/img:/snapshot" "tezos/tezos:latest-release" tezos-snapshot-import # --data-dir "/var/run/tezos/node/data" #--config-file "/config/config.json"

docker run -d -v "$PWD:/var/run/tezos/" --network="host" --name "tezos-node-$4" "tezos/tezos:latest-release" tezos-node --network "$1" --cors-header='content-type' --cors-origin='*' --rpc-addr 127.0.0.1:"$2" --net-addr 127.0.0.1:"$3" --history-mode "$5" #--data-dir "/var/run/tezos/node/data" # --config-file "/config/config.json"

rm img