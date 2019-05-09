# Nautilus

Automation tools for deploying blockchain networks

## Prerequisites
Prior to using this script, it's required that docker, sbt, and openjdk are installed on the host.  
In order to install Docker, please execute the following commands:

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo apt-key fingerprint 0EBFCD88
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io -y

Depending on the use case, it might be advisable, though not required to add the user executing these commands to the docker group. 

In order to install sbt and openjdk, please execute the following commands:

sudo apt-get install -y openjdk-8-jdk-headless
echo "deb https://dl.bintray.com/sbt/debian /" | sudo tee -a /etc/apt/sources.list.d/sbt.list
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2EE0EA64E40A89B84B2DF73499E82A75642AC823
sudo apt-get update
sudo apt-get install -y sbt


## Initialize Environment

This script builds and deploys a conseil, postgres, and/or tezos container.  Please note, in order to run the containers, ports 1337(conseil front end), 8732(tezos rpc), and 9732(tezos network)  will need to be opened.  

In this repo, there is provided a default configuration for all three containers, this config folder is located in docker/config/local.  These configuration values can be changed, it's advisable, but not required to copy the config folder to another location so that the original can be kept intact for reference purposes.    

The default network for tezos is alphanet, and this setting is stored in https://github.com/Cryptonomic/Nautilus/blob/master/docker/config/local/tezos/tezos_network.txt This text file only contains one word, currently it's "alphanet".  However, it can be changed to mainnet or zeronet.  

The default configuration for conseil and postgres is contained in /path/to/repo/docker/config/local/conseil/conseil.conf.    
## Run Script

Depending on the use case the following commands will build the images and deploy the containers.  Please note that the name of the containers will depend on the name of the folder containing the config files, in the default case the folder is "local", so the containers will be named conseil-local, postgres-local, and tezos-node-local.  

### Running with default configs
Build all three containers:
```bash /path/to/repo/docker/nautilus.sh -a```

Please note, the following flags can be used together or seperately.


    -b, --custom-build-path        specify a custom working directory to use for the build instance, defaults to
                                   $HOME/nautilus/current-date-time
                                   
    -c, --conseil                  stops and removes existing conseil container if it exists
                                   and rebuilds and starts a new instance of the conseil container
    -d, --database                 stops and removes existing postgres database container if it exists  
    -p, --path_to_config           absolute path to configuration folder, folder should contain at the very least a conseil                                    folder,if using a modified schema, a postgres folder with a conseil.sql file. if not                                        specified,uses configuration files for conseil, postgres and tezos from the config folder                                    in repo.  config folder name will also be used in docker container nomenclature(e.g.                                        config folder name is prod1, docker container name will be conseil-prod1, postgres-prod1,                                    etc.),default config folder is "local", it resides within config folder in repo
                                   NOTE: docker volumes will be created here to create persistence
    -t, --tezos                    stops and removes existing tezos container if it exists
                                   and rebuilds and starts the tezos container
Build conseil container seperately
```bash /path/to/repo/docker/nautilus.sh -c```
Build conseil container seperately with customized config files at a seperate location.
```bash /path/to/repo/docker/nautilus.sh -c -p /path/to/config-folder```
Build conseil and postgres container seperately with custom working directory and custom config files
```bash /path/to/repo/docker/nautilus.sh -c -p /path/to/config-folder -b /path/to/working/directory```

These commands will build the images as well as deploy the containers.

### Stop Environment

To stop any of the individual containers will require the use of docker commands. 
Presuming default configuration
```docker container stop conseil-local``` 
This will stop the conseil-local container. 
```docker container rm conseil-local```
This will remove the conseil-local container, please note, if removing the container, recreating the container will require that the ports required to make the container function.

If the containers have been removed, the following commands will recreate the containers:

For conseil:
```docker run --name=conseil-local --network=nautilus -d -p 1337:1337 conseil-local```
In this case "conseil-local" would be the name of the docker image that is being used to create the container.

For postgres:
```docker run --name=postgres-local --network=nautilus -v pgdata-local:/var/lib/postgresql/data -d -p 5432:5432 postgres-local```

For tezos:
```docker run --name=tezos-node-local --network=nautilus -v tznode_data:/var/run/tezos/node-local -v tzclient_data:/var/run/tezos/client-local -d -p 8732:8732 -p 9732:9732 tezos-node-local```








