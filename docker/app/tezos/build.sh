 #!/bin/bash

cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd
. ../parse_opt.sh

TEZOS_WORK_DIR="$HOME/tezos_build_$BUILD_NAME"
mkdir "$TEZOS_WORK_DIR"
cp ./dockerfile "$TEZOS_WORK_DIR"/dockerfile
cd $TEZOS_WORK_DIR
sed 's/protocol/"$tezosprotocol"/g' dockerfile

docker build -f dockerfile -t tezos-node-"$DEPLOYMENT_ENV" .

