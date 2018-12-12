java -Xms2048m -Xmx3g -Dconfig.file=conseil.conf -cp conseil.jar tech.cryptonomic.conseil.Lorre alphanet | tee lorre.log &

java -Xms512m -Xmx1g -Dconfig.file=conseil.conf -cp conseil.jar tech.cryptonomic.conseil.Conseil &
