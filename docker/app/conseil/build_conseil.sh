#!/bin/bash
#
# Container build script for conseil





build_conseil () {

    DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

    DEPLOYMENT_ENV="$1"
    WORKING_DIR="$2"
    PATH_TO_CONFIG="$3"
    build_time="$4"

    current_continer=conseil-"$DEPLOYMENT_ENV"

	docker container stop "$current_continer"
	docker container rm "$current_continer"

	CONSEIL_WORK_DIR="$WORKING_DIR"/conseil-"$DEPLOYMENT_ENV"
    mkdir "$CONSEIL_WORK_DIR"
    cd "$CONSEIL_WORK_DIR"

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



    cp "$PATH_TO_CONFIG"/conseil/conseil.conf ./conseil.conf
    cp "$PATH_TO_CONFIG"/conseil/runconseil-lorre.sh ./runconseil-lorre.sh
    conseil_conf_file=./conseil.conf
    runconseillorre=./runconseil-lorre.sh

    {
    read line1
    read line2
    read line3
    read line4
    read line5
    } < "$PATH_TO_CONFIG"/conseil/credentials.txt
    line1=`echo "$line1"`
    line2=`echo "$line2"`
    line3=`echo "$line3"`
    line4=`echo "$line4"`
    line5=`echo "$line5"`
    sed -i "s/databaseName=.*/$line1/g" "$conseil_conf_file"
    sed -i "s/user=.*/$line2/g" "$conseil_conf_file"
    sed -i "s/password=.*/$line3/g" "$conseil_conf_file"
    sed -i "s/keys.=...APIKEY..*/$line4/g" "$conseil_conf_file"
    sed -i "s/alphanet/$line5/g" "$runconseillorre"
    cp "$conseil_conf_file" ./build/
    cp "$runconseillorre" ./build/




    cp ./Conseil/src/main/resources/logback.xml ./build/
    #cp "$PATH_TO_CONFIG"/conseil/runconseil-lorre.sh ./build/


    docker build -f "$DIR"/dockerfile -t conseil-"$DEPLOYMENT_ENV" .
    rm ./build
   	docker run --name=conseil-"$DEPLOYMENT_ENV" --network=nautilus -d -p 1337:1337 conseil-"$DEPLOYMENT_ENV"
    (( $? == 0 )) || fatal "Unable to build conseil container"
	yes | docker system prune
}