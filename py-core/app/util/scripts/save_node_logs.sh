#!/bin/bash

name=$1

cd "util/docker-compose/$name" || exit 1

touch log.tzlog

docker-compose logs --tail="100" > log.tzlog