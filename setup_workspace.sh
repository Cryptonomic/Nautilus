#!/bin/bash

mkdir ~/.nautilus-core

# Pull Tezos Docker Image
docker pull tezos/tezos:latest-release

#docker pull tezos/tezos:ebetanet-release

# Pull Redis Docker Container for Python Job Queue
docker pull redis

# Build Mainnet Arronax Image Locally
git clone https://github.com/Cryptonomic/Arronax.git

cd Arronax

touch src/config.tsx

echo "import { Config } from './types';

const configs: Config[] = [
  {
    platform: 'tezos',
    network: 'mainnet',
    displayName: 'Tezos Mainnet',
    url: 'http://conseil-api:80',
    apiKey: 'conseil',
    nodeUrl: 'http://tezos-node:8732',
    entities: ['blocks', 'operations', 'accounts', 'bakers', 'governance'],
    hiddenEntities: ['originated_account_maps', 'big_maps', 'big_map_contents']
  }
]

export default configs;
" >> src/config.tsx

npm i

docker build -t arronax-mainnet .

# shellcheck disable=SC2103
cd ..

rm -rf Arronax

# Build Delphinet Arronax Image Locally
git clone https://github.com/Cryptonomic/Arronax.git

cd Arronax

touch src/config.tsx

echo "import { Config } from './types';

const configs: Config[] = [
  {
    platform: 'tezos',
    network: 'delphinet',
    displayName: 'Tezos Delphi',
    url: 'http://conseil-api:80',
    apiKey: 'conseil',
    nodeUrl: 'http://tezos-node:8732',
    entities: ['blocks', 'operations', 'accounts', 'bakers', 'governance'],
    hiddenEntities: ['originated_account_maps', 'big_maps', 'big_map_contents']
  }
]

export default configs;
" >> src/config.tsx

npm i

docker build -t arronax-delphinet .

# shellcheck disable=SC2103
cd ..

rm -rf Arronax

#Build Edonet Arronax Image Locally
git clone https://github.com/Cryptonomic/Arronax.git

cd Arronax

touch src/config.tsx

echo "import { Config } from './types';

const configs: Config[] = [
  {
    platform: 'tezos',
    network: 'edonet',
    displayName: 'Tezos Mainnet',
    url: 'http://conseil-api:80',
    apiKey: 'conseil',
    nodeUrl: 'http://tezos-node:8732',
    entities: ['blocks', 'operations', 'accounts', 'bakers', 'governance'],
    hiddenEntities: ['originated_account_maps', 'big_maps', 'big_map_contents']
  }
]

export default configs;
" >> src/config.tsx

npm i

docker build -t arronax-edonet .

# shellcheck disable=SC2103
cd ..

rm -rf Arronax

# Build Edo2Net Arronax Image Locally
git clone https://github.com/Cryptonomic/Arronax.git

cd Arronax

touch src/config.tsx

echo "import { Config } from './types';

const configs: Config[] = [
  {
    platform: 'tezos',
    network: 'edo2net',
    displayName: 'Tezos Mainnet',
    url: 'http://conseil-api:80',
    apiKey: 'conseil',
    nodeUrl: 'http://tezos-node:8732',
    entities: ['blocks', 'operations', 'accounts', 'bakers', 'governance'],
    hiddenEntities: ['originated_account_maps', 'big_maps', 'big_map_contents']
  }
]

export default configs;
" >> src/config.tsx

npm i

docker build -t arronax-edo2net .

# shellcheck disable=SC2103
cd ..

rm -rf Arronax

# Build Falphanet Arronax Image Locally
git clone https://github.com/Cryptonomic/Arronax.git

cd Arronax

touch src/config.tsx

echo "import { Config } from './types';

const configs: Config[] = [
  {
    platform: 'tezos',
    network: 'falphanet',
    displayName: 'Tezos Mainnet',
    url: 'http://conseil-api:80',
    apiKey: 'conseil',
    nodeUrl: 'http://tezos-node:8732',
    entities: ['blocks', 'operations', 'accounts', 'bakers', 'governance'],
    hiddenEntities: ['originated_account_maps', 'big_maps', 'big_map_contents']
  }
]

export default configs;
" >> src/config.tsx

npm i

docker build -t arronax-falphanet .

# shellcheck disable=SC2103
cd ..

rm -rf Arronax