#!/bin/bash
#
# Container build script for conseil

#cd "$HOME"

if [[ -d ./Conseil ]] ; then
    cd Conseil
    git pull
else
    git clone https://github.com/Cryptonomic/Conseil.git
    cd Conseil
fi


sbt 'set logLevel in compile := Level.Error' compile
sbt 'set test in assembly := {}' assembly

cd ..

ln -s ./Conseil ./build
(( $? == 0 )) || fatal "Unable to create symlink to build directory"
mv /tmp/conseil.jar ./build/conseil.jar
cp ./Conseil/src/main/resources/application.conf ./build/