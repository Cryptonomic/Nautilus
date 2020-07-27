#!/bin/bash

cd "util/tezos-nodes/data/$1"

git clone https://github.com/Cryptonomic/Arronax.git

cd Arronax

#git checkout master

#sed -i "s/EXPOSE 80/EXPOSE $2/g" Dockerfile

#sed -i "s/listen 80;/listen $2;/g" default.conf

touch src/config.tsx

echo "import { Config } from './types';

const configs: Config[] = [
  {
    platform: 'tezos',
    network: 'mainnet',
    displayName: 'Tezos Mainnet',
    url: 'http://localhost:$4',
    apiKey: 'conseil',
    nodeUrl: 'http://tezos-node:8732',
    entities: ['blocks', 'operations', 'accounts', 'bakers', 'governance'],
    hiddenEntities: ['originated_account_maps', 'big_maps', 'big_map_contents']
  }
]

export default configs;
" >> src/config.tsx

docker build -t arronax .

