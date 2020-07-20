#!/bin/bash

docker rm "conseil-api-$1"

docker rm "conseil-lorre-$1"

docker rm "conseil-postgres-$1"

docker rm "arronax-$1"

docker rm "tezos-node-$1"

rm -rf "util/tezos-nodes/data/$1"

#rm -f "/util/tezos-nodes/config/$1.json"