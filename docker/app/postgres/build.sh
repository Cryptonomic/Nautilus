#!/bin/bash

#check out schema and put it in the right place

wget https://raw.githubusercontent.com/Cryptonomic/Conseil/master/doc/conseil.sql
docker build -f dockerfile -t postgres-$1 .


