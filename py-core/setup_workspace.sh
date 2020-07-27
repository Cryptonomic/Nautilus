#!/bin/bash

# Pull Tezos Docker Image
docker pull tezos/tezos:latest-release

# Build Arronax Image Locally
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

docker build -t arronax .

# shellcheck disable=SC2103
cd ..

rm -rf Arronax
