#!/bin/bash

docker run -d --network="host" --name "arronax-$1" "arronax-$1"