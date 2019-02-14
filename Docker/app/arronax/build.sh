#!/bin/bash
mkdir $1-temp && cd $1-temp

git clone https://github.com/Cryptonomic/Arronax.git
cd Arronax

npm install

cp -f ../../env/$1/config.json ./public

npm run build

docker build -f ./dockerfile -t arronax-$1 .
