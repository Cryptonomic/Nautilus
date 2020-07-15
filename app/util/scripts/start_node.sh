#!/bin/bash

cd util

mkdir tezos-nodes

cd tezos-nodes

mkdir data

cd data

mkdir "$4"

cd "$4"

touch "$4.tzlog"

docker run -d --network="host" --name "tezos-node-$4" "tezos/tezos:$1" tezos-node --cors-header='content-type' --cors-origin='*' --rpc-addr 127.0.0.1:"$2" --net-addr 127.0.0.1:"$3" --history-mode "$5"

#./tezos-node config --config-file ../tezos-nodes/config/"$4".json reset

#./tezos-node config --data-dir ../tezos-nodes/data/"$4" --network "$1" --config-file ../tezos-nodes/config/"$4".json init

#./tezos-node config --data-dir ../tezos-nodes/data/"$4" --network "$1" --config-file ../tezos-nodes/config/"$4".json --cors-header='content-type' --cors-origin='*' --rpc-addr 127.0.0.1:"$2" --net-addr 127.0.0.1:"$3" update

#./tezos-node identity --data-dir ../tezos-nodes/data/"$4" --config-file ../tezos-nodes/config/"$4".json generate

#screen -dm -S "$4" ./tezos-node run --data-dir ../tezos-nodes/data/"$4" --config-file ../tezos-nodes/config/"$4".json --network "$1" --rpc-addr 127.0.0.1:"$2" --net-addr 127.0.0.1:"$3" --history-mode "$5"

#export node_pid=$(screen -ls | awk '/\."$4"\t/ {print strtonum($1)}')
