 #!/bin/bash

#check out schema and put it in the right place

docker build -f dockerfile -t postgres-$1 .

yes | docker system prune

#docker run --rm -it --entrypoint=/bin/sh postgres-local
#docker build -f dockerfile -t postgres-local .
#docker run -d -p 5432:5432 postgres-local