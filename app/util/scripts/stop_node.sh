#!/bin/bash

docker stop "tezos-node-$1"

#screen -XS "$1" quit