#!/bin/sh

java -Xms512m -Xmx14g -Dconfig.file=conseil.conf -cp conseil.jar tech.cryptonomic.conseil.Lorre alphanet &

java -Xms512m -Xmx2g -Dconfig.file=conseil.conf -cp conseil.jar tech.cryptonomic.conseil.Conseil
