#!/bin/bash
current_time = $(date "+%Y.%m.%d-%H.%M.%S")

if $2 <> ''; then
    path_to_config = $2
else
    path_to_config = $(pwd)



mkdir ~/build_$current_time
work_dir = ~/build_$current_time

docker container rm postgres-$1
docker container rm tezos-node-$1
docker container rm conseil-$1
docker container rm arronax-$1

docker volume rm pgdata-$1
docker volume rm tznode_data-$1
docker volume rm tzclient_data-$1

cd $2/app/conseil
. ./build.sh $1 path_to_config work_dir
cd ../..

cd $2/app/tezos
. ./build.sh $1 path_to_config work_dir
cd ../..

cd $2/app/postgres
. ./build.sh $1 path_to_config work_dir
cd ../..

docker network create nautilus
#volumes have to be constant and as such cannot be included in the build directory
mkdir /path_to_config/volumes
mkdir /path_to_config/volumes/pgdata-$1
mkdir /path_to_config/volumes/tznode_data-$1
mkdir /path_to_config/volumes/tzclient_data-$1
docker volume create --driver local --opt type=none --opt o=bind --opt device=/path_to_config/volumes/pgdata-$1 pgdata-$1
docker volume create --driver local --opt type=none --opt o=bind --opt device=/path_to_config/volumes/tznode_data-$1 tznode_data-$1
docker volume create --driver local --opt type=none --opt o=bind --opt device=/path_to_config/volumes/tzclient_data-$1 tzclient_data-$1


docker run --name=postgres-$1 --network=nautilus -v pgdata-$1:/var/lib/postgresql/data -d -p 5432:5432 postgres-$1
docker run --name=tezos-node-$1 --network=nautilus -v tznode_data:/var/run/tezos/node-$1 -v tzclient_data:/var/run/tezos/client-$1 -d -p 8732:8732 -p 9732:9732 tezos-node-$1
docker run --name=conseil-$1 --network=nautilus -d -p 1337:1337 conseil-$1


yes | docker system prune
