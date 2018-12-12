 #!/bin/bash

cd ./app/tezos
. ./build.sh $1
cd ../..

cd ./app/postgres
. ./build.sh $1
cd ../..

cd ./app/conseil
. ./build.sh $1
cd ../..

cd ./app/arronax
. ./build.sh $1
cd ../..

docker network create nautilus

#docker run --name=postgres-$1 --network=nautilus -d -p 5432:5432 postgres-$1
#docker run --name=tezos-node-$1 --network=nautilus -d -p 8732:8732 tezos-node-$1
#docker run --name=conseil-$1 --network=nautilus -d -p 1337:1337 conseil-$1 /conseil/runconseil.sh
#docker run --name=arronax-$1 --network=nautilus -d -p 8080:80 arronax-$1
