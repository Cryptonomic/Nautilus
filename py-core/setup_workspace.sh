#!/bin/bash

mkdir ~/.nautilus-core

# Pull Tezos Docker Image
docker pull tezos/tezos:latest-release

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

docker build -t arronax-mainnet .

# shellcheck disable=SC2103
cd ..

rm -rf Arronax

# Build Carthagenet Arronax Image Locally
git clone https://github.com/Cryptonomic/Arronax.git

cd Arronax

touch src/config.tsx

echo "import { Config } from './types';

const configs: Config[] = [
  {
    platform: 'tezos',
    network: 'carthagenet',
    displayName: 'Tezos Carthagenet',
    url: 'http://conseil-api:80',
    apiKey: 'conseil',
    nodeUrl: 'http://tezos-node:8732',
    entities: ['blocks', 'operations', 'accounts', 'bakers', 'governance'],
    hiddenEntities: ['originated_account_maps', 'big_maps', 'big_map_contents']
  }
]

export default configs;
" >> src/config.tsx

docker build -t arronax-carthagenet .

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

docker build -t arronax-delphinet .

# shellcheck disable=SC2103
cd ..

rm -rf Arronax
