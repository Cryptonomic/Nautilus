mkdir $1-temp && cd $1-temp

git clone https://github.com/Cryptonomic/Arronax.git
cd Arronax
git checkout develop

npm install

cp -f ../../env/$1/config.json ./public

npm run build

docker build -f ../../dockerfile -t arronax-$1 .
yes | docker system prune

#docker build -f dockerfile -t arronax-local .

#docker run -d -p 80:80 arronax-local
#docker run -d -p 80:3000 arronax-local

#docker run --rm -it --entrypoint=/bin/bash arronax-local
#docker exec -t -i arronax-local /bin/bash


