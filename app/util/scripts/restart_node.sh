#!/bin/bash

docker start "tezos-node-$4"

#cd util/tezos

#./tezos-node identity --data-dir ../tezos-nodes/data/"$4" --config-file ../tezos-nodes/config/"$4".json generate

#screen -dm -S "$4" ./tezos-node run --data-dir ../tezos-nodes/data/"$4" --config-file ../tezos-nodes/config/"$4".json --network "$1" --rpc-addr 127.0.0.1:"$2" --net-addr 127.0.0.1:"$3" --history-mode "$5"
