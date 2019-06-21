# Nautilus

Automation tools for deploying reproducible blockchain infrastructure.

## Running Conseil for Tezos

This document assumes there is a Tezos node running and shows how to setup containers for [Conseil](https://github.com/Cryptonomic/Conseil) and Postgres respectively.

### Prerequisites
1. A Linix system, we use Ubuntu LTS releases.
1. Docker installed and a non-root user added to the docker group in order to run the docker commands.
1. A Scala build environment which can be installed as follows:
```sh
sudo apt-get install -y openjdk-8-jdk-headless
echo "deb https://dl.bintray.com/sbt/debian /" | sudo tee -a /etc/apt/sources.list.d/sbt.list
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2EE0EA64E40A89B84B2DF73499E82A75642AC823
sudo apt-get update
sudo apt-get install -y sbt
```

### Image creation
1. Clone nautilus repo from github: 
    ```sh
    git clone https://github.com/Cryptonomic/Nautilus.git ./nautilus
    cd nautilus
    ```
1.   There are two ways to configure the installation for the Conseil and Postgres containers,  there is a default config that’s provided as part of the repo and as an alternative you can provide your own installation, for the sake of this document we will use the provided installation and modify it slightly to allow it to work with the user’s infrastructure.
1. In the `conseil.conf` [file](https://github.com/Cryptonomic/Nautilus/blob/master/docker/config/local/conseil/conseil.conf) located in the repo at path `/docker/config/local/conseil/conseil.conf`
Some changes are required, specifically, if running mainnet, “alphanet” needs to be changed to "mainnet", also, the hostname needs to be changed to match the IP of the node running Tezos as shown below.

```json
"platforms": {
    "tezos": {
        "mainnet": {
            "node": {
                "protocol": "http",
                "hostname": "1.2.3.4",
                "port": 8732,
                "pathPrefix": ""
            }
        }
    }
}
```

If changing the Postgres username and password, it needs to be changed in the `conseil.conf` file as well as the `env.list` file in the repo. The `env.list` [file](https://github.com/Cryptonomic/Nautilus/blob/master/docker/config/local/postgres/env.list).
Within the downloaded repo, it is in `/docker/config/local/postgres/env.list`.

`databasename`, `username`, and `password` in `conseil.conf` must match `CONSEILDB_DBNAME`, `CONSEILDB_USER`, and `CONSEILDB_PASSWORD` in `env.list`.

4. Build Postgres and Conseil containers for Docker.
```sh
bash /path/to/repo/Nautilus/docker/nautilus.sh -c -d
```

The `-c` flag builds and packages Conseil docker image. `-d` Does the same for Postgres, these flags can be applied separately as well.
```sh
 bash /path/to/repo/Nautilus/docker/nautilus.sh -c
 bash /path/to/repo/Nautilus/docker/nautilus.sh -d
 ```

Note that the containers are named after the directories immediately inside `/docker/config/`, for example `conseil-local`.

### Running the environment

While the script in step 4 will spawn the images created at the end, starting them later can be done as follows.

```sh
docker run --name=postgres-local -v pgdata-local:/var/lib/postgresql/data -d -p 5432:5432 postgres-local
docker run --name=conseil-local -d -p 1337:1337 conseil-local
```

To stop the containers execute:

```sh
docker container stop conseil-local
docker container stop postgres-local

```

For more details visit the [Conseil repo](https://github.com/Cryptonomic/Conseil) on GitHub. [Developer documentation](https://cryptonomic.github.io/Conseil/#/) is also available with specific usage examples.
