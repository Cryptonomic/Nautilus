#!/bin/bash
if "$1" = local  ; then
 echo 'Building Environment "'$1'"'

 docker container rm postgres-$1
 docker container rm tezos-node-$1
 docker container rm conseil-$1
 docker container rm arronax-$1

 docker volume rm pgdata-$1
 docker volume rm tznode_data-$1
 docker volume rm tzclient_data-$1

 cd ./app/conseil
 . ./build.sh $1
 cd ../..

 cd ./app/tezos
 . ./build.sh $1
 cd ../..

 cd ./app/postgres
 . ./build.sh $1
 cd ../..

 docker network create nautilus

 mkdir ./volumes
 mkdir ./volumes/pgdata-$1
 mkdir ./volumes/tznode_data-$1
 mkdir ./volumes/tzclient_data-$1
 docker volume create --driver local --opt type=none --opt o=bind --opt device=/$(pwd)/volumes/pgdata-$1 pgdata-$1
 docker volume create --driver local --opt type=none --opt o=bind --opt device=/$(pwd)/volumes/tznode_data-$1 tznode_data-$1
 docker volume create --driver local --opt type=none --opt o=bind --opt device=/$(pwd)/volumes/tzclient_data-$1 tzclient_data-$1


 docker run --name=postgres-$1 --network=nautilus -v pgdata-$1:/var/lib/postgresql/data -d -p 5432:5432 postgres-$1
 docker run --name=tezos-node-$1 --network=nautilus -v tznode_data:/var/run/tezos/node-$1 -v tzclient_data:/var/run/tezos/client-$1 -d -p 8732:8732 -p 9732:9732 tezos-node-$1
 docker run --name=conseil-$1 --network=nautilus -d -p 1337:1337 conseil-$1


 yes | docker system prune

else
 docker container rm postgres-$1
 docker container rm tezos-node-$1
 docker container rm conseil-$1
 docker container rm arronax-$1

 docker volume rm pgdata-$1
 docker volume rm tznode_data-$1
 docker volume rm tzclient_data-$1

 cd $2./app/conseil
 . ./build.sh $1 $2
 cd ../..

 cd $2./app/tezos
 . ./build.sh $1 $2
 cd ../..

 cd $2./app/postgres
 . ./build.sh $1 $2
 cd ../..

 docker network create nautilus

 mkdir ./volumes
 mkdir ./volumes/pgdata-$1
 mkdir ./volumes/tznode_data-$1
 mkdir ./volumes/tzclient_data-$1
 docker volume create --driver local --opt type=none --opt o=bind --opt device=/$2/volumes/pgdata-$1 pgdata-$1
 docker volume create --driver local --opt type=none --opt o=bind --opt device=/$2/volumes/tznode_data-$1 tznode_data-$1
 docker volume create --driver local --opt type=none --opt o=bind --opt device=/$2/volumes/tzclient_data-$1 tzclient_data-$1


 docker run --name=postgres-$1 --network=nautilus -v pgdata-$1:/var/lib/postgresql/data -d -p 5432:5432 postgres-$1
 docker run --name=tezos-node-$1 --network=nautilus -v tznode_data:/var/run/tezos/node-$1 -v tzclient_data:/var/run/tezos/client-$1 -d -p 8732:8732 -p 9732:9732 tezos-node-$1
 docker run --name=conseil-$1 --network=nautilus -d -p 1337:1337 conseil-$1


 yes | docker system prune


fi
