#!/bin/bash
#
# Container build script for conseil

cd "$HOME"

if [[ -d ./Conseil ]] ; then
    cd Conseil
    git pull
else
    git clone https://github.com/Cryptonomic/Conseil.git
    cd Conseil
fi

cp "$PATH_TO_CONFIG"/conseil/* "$CONSEIL_WORK_DIR"/
cp "$HOME"/Conseil/* "$CONSEIL_WORK_DIR"/

cd "$CONSEIL_WORK_DIR"
sbt 'set logLevel in compile := Level.Error' compile
sbt 'set test in assembly := {}' assembly

ln -s "$CONSEIL_WORK_DIR" ./build
mv /tmp/conseil.jar ./build/conseil.jar



#ln -s $HOME/Conseil "$CONSEIL_WORK_DIR"/build
#mv /tmp/conseil.jar "$CONSEIL_WORK_DIR"/build/conseil.jar
