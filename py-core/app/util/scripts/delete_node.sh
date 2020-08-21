#!/bin/bash

name=$1

cd "util/docker-compose/$name" || exit 1

docker-compose down