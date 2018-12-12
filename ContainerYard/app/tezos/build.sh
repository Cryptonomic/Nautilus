 #!/bin/bash

docker build -f dockerfile -t tezos-node-$1 .
#docker run --rm -it --entrypoint=/bin/sh tezos-node-local
#docker run -d -p 8732:8732 tezos-node-local

yes | docker system prune
