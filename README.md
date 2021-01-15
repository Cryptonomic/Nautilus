# Nautilus Core

Naultilus Core is a tool to automate running Tezos Nodes. It allows customization of the most important node features, and easily running multiple nodes, along with different integrations to simplfy node interactions.

With each Node in Archive mode, you can also start an instance of [Conseil](https://github.com/Cryptonomic/Conseil) and [Arronax](https://arronax.io).

Nautilus Core is only supported in macOS and Linux. 

## Prerequisites:

### System Requirements

Running Tezos Nodes (particularly Archive Nodes) can take massive amounts of storage when fully synced (~300 GB).
16GB of memory is recommended for running Tezos Nodes, along with the other processes alongside it. 
8GB of ram should suffice, but it might not be comfortable for the containers, nor for anything else runnign on the machine.

### Software Requirements

You need to have `wget`, `git`, `python3`, `docker`, `docker-compose`, `openssl`, and `pip3` installed.

The `docker` config should be set up with a `docker` user with sudo privileges, so that the app can run without running as root.

These can all be installed with:

```shell
sudo apt-get install wget
sudo apt-get install git
sudo apt-get install python3
sudo apt-get install python3-venv
sudo apt-get install python3-pip
sudo apt-get install openssl
sudo apt-get install docker
sudo apt-get install docker-compose
sudo groupadd docker
sudo usermod -a -G docker $MY_USER
```

The app runs inside a python `venv` so it will not add anything to your system environment.

Officially Tested with Software Versions:
```
wget - 1.20.3
git - 2.25.1
python3 - 3.9
python3-venv - default installed with python3
python3-pip - 20.3.1
openssl - 2.8.3
docker - 20.10.2
docker-compose - 1.27.4
```

## Running Instructions:

Clone the project, and run `./setup_workspace.sh`, which will download docker images, and build Arronax docker images for the different networks.

After setup, you can run `./start.sh` in the root directory of the project, and visit http://localhost:4104 to see the running UI.

We recommend that you do NOT interact with the nodes without the UI, as this can lead to discrepancies between your system, and the script.

Please only start and stop nodes from the UI.

## Troubleshooting

If there is a node which is shown to be running on the app, but is not actually running on your computer, you can click "restart" to resync the UI with your computer.

Use `docker ps` to list all of the docker containers running on your computer. You should be able to see the containers started by the app. 

## Uninstall / Cleanup:

Deleting the repository will delete all of the locally stored data.

Docker images will be generated, which can be removed using docker's CLI. All of the images generated have the names `conseil-api-foo`, `conseil-lorre-foo`, or `arronax-foo` where `foo` is the name of the nodes installed.

