#!/bin/bash

name=$1

cd "$HOME/.nautilus-core/$name" || exit 1

docker-compose up -d --remove-orphans