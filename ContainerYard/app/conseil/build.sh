 #!/bin/bash

mkdir $1-temp && cd $1-temp

git clone https://github.com/Cryptonomic/Conseil.git
cd Conseil
sbt compile
sbt assembly

cd ../..
ln -s ./$1-temp/Conseil ./build

#mv ./$1-temp/Conseil/target/scala-2.12/conseil_*.jar ./build/conseil.jar
mv /tmp/conseil.jar ./build/conseil.jar
cp ./env/$1/conseil.conf ./build/
cp ./env/$1/logback.xml ./build/
cp ./env/$1/runconseil.sh ./build/

docker build -f dockerfile -t conseil-$1 .

rm ./build

yes | docker system prune

#docker run -d -p 1337:1337 --network="host" conseil-local /conseil/runconseil.sh
#docker run --rm -it --network="host" --entrypoint=/bin/sh conseil-local
#docker exec -t -i conseil-local /bin/sh

#docker run --name=conseil-dev --network=nautilus -d -p 1337:1337 conseil-dev /conseil/runconseil.sh
#docker run --rm -it --name=conseil-local --network=nautilus --entrypoint=/bin/sh conseil-dev