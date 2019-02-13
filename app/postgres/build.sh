#!/bin/bash

#check out schema and put it in the right place
wget https://github.com/Cryptonomic/Conseil/blob/master/doc/conseil.sql
docker build -f dockerfile -t postgres-$1 .


