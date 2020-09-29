#!/bin/bash

name=$1

cd "util/docker-compose/$name" || exit 1

touch log.tzlog

docker-compose logs --tail="100" > log.tzlog

touch conseil-log.tzlog

docker-compose logs --tail="100" conseil-api > conseil-log.tzlog

touch lorre-log.tzlog

docker-compose logs --tail="100" conseil-lorre > lorre-log.tzlog

touch arronax-log.tzlog

docker-compose logs --tail="100" arronax > arronax-log.tzlog

touch node-log.tzlog

docker-compose logs --tail="100" tezos-node > node-log.tzlog

touch postgres-log.tzlog

docker-compose logs --tail="100" conseil-postgres > postgres-log.tzlog