 #!/bin/bash

cd /path_to_config/tezos

docker build -f dockerfile -t tezos-node-$1 .

