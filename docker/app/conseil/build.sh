#!/bin/bash
#
# Container build script for conseil

cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd
#runs parse_opt script in current shell(sourcing)
. ../parse_opt.sh


CONSEIL_WORK_DIR="$HOME/conseil_build_$BUILD_NAME"
mkdir "$CONSEIL_WORK_DIR"

cd $HOME

if [[ -d ./Conseil ]] ; then
    cd Conseil
    git pull
else
    git clone https://github.com/Cryptonomic/Conseil.git
    cd Conseil
fi

sbt 'set logLevel in compile := Level.Error' compile
sbt 'set test in assembly := {}' assembly

cd $CONSEIL_WORK_DIR
ln -s $HOME/Conseil ./build
(( $? == 0 )) || fatal "Unable to create symlink to build directory"

cp $HOME/Conseil/src/main/resources/application.conf ./build/
cp $HOME/Conseil/src/main/resources/logback.xml ./build/

mv /tmp/conseil.jar ./build/conseil.jar

cp /$PATH_TO_CONFIG/conseil/conseil.conf ./build/
cp /$PATH_TO_CONFIG/conseil/runconseil-lorre.sh ./build/

docker build -f $DIR/docker/app/conseil/dockerfile -t conseil-$DEPLOYMENT_ENV .

rm ./build
