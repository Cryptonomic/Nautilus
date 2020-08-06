import wget
import tarfile
import os
import shutil

from util.app_functions import *

SCRIPT_FILE_PATH = "./util/scripts/"
DOCKER_COMPOSE_FILE_PATH = "util/docker-compose/"

# TODO: CHANGE THESE LINKS
# Snapshot Download URLs
MAINNET_FULL_SNAPSHOT = "https://conseil-snapshots.s3.amazonaws.com/tezos-node_snapshot-latest.full"
MAINNET_ROLLING_SNAPSHOT = "https://conseil-snapshots.s3.amazonaws.com/tezos-node_snapshot-latest.full"
CARTHAGENET_FULL_SNAPSHOT = "https://conseil-snapshots.s3.amazonaws.com/tezos-node_snapshot-latest.full"
CARTHAGENET_ROLLING_SNAPSHOT = "https://conseil-snapshots.s3.amazonaws.com/tezos-node_snapshot-latest.full"

# Data-Directory Download URLs
MAINNET_DATA_DIR = "https://conseil-snapshots.s3.amazonaws.com/tezos-data.tar.gz"
CARTHAGENET_DATA_DIR = "https://conseil-snapshots.s3.amazonaws.com/tezos-data.tar.gz"


def create_node(data):

    data_location = DOCKER_COMPOSE_FILE_PATH + data["name"]
    filename = ""

    # Start Node
    if data["restore"]:
        shutil.copytree(DOCKER_COMPOSE_FILE_PATH + "reference-snapshot", DOCKER_COMPOSE_FILE_PATH + data["name"])

        if data["network"] == "mainnet" and data["history_mode"] == "archive":
            filename = wget.download(MAINNET_DATA_DIR, data_location)

        if data["network"] == "mainnet" and data["history_mode"] == "full":
            filename = wget.download(MAINNET_FULL_SNAPSHOT, data_location)

        if data["network"] == "mainnet" and data["history_mode"] == "rolling":
            filename = wget.download(MAINNET_ROLLING_SNAPSHOT, data_location)

        if data["network"] == "carthagenet" and data["history_mode"] == "archive":
            filename = wget.download(CARTHAGENET_DATA_DIR, data_location)

        if data["network"] == "carthagenet" and data["history_mode"] == "full":
            filename = wget.download(CARTHAGENET_FULL_SNAPSHOT, data_location)

        if data["network"] == "carthagenet" and data["history_mode"] == "rolling":
            filename = wget.download(CARTHAGENET_ROLLING_SNAPSHOT, data_location)

        if data["history_mode"] == "archive":
            file = tarfile.open(data_location + "/tezos-data.tar.gz")
            file.extractall(data_location)
            file.close()
            os.remove(data_location + "/tezos-data.tar.gz")
        else:
            docker_volumes = dict()

            docker_volumes[os.getcwd() + DOCKER_COMPOSE_FILE_PATH + data["name"] + "/tezos-data"] = dict()
            docker_volumes[os.getcwd() + DOCKER_COMPOSE_FILE_PATH + data["name"] + "/tezos-data"]["bind"] = "/var/run/tezos"
            docker_volumes[os.getcwd() + DOCKER_COMPOSE_FILE_PATH + data["name"] + "/tezos-data"]["mode"] = "rw"

            docker_volumes[os.getcwd() + DOCKER_COMPOSE_FILE_PATH + data["name"] + "/" + filename] = dict()
            docker_volumes[os.getcwd() + DOCKER_COMPOSE_FILE_PATH + data["name"] + "/" + filename]["bind"] = "/snapshot"
            docker_volumes[os.getcwd() + DOCKER_COMPOSE_FILE_PATH + data["name"] + "/" + filename]["mode"] = "rw"

            docker_client = docker.from_env()
            docker_client.containers.run("tezos/tezos:latest-release",
                                         "tezos-snapshot-import",
                                         auto_remove=True,
                                         volumes=docker_volumes
                                         )
    else:
        shutil.copytree(DOCKER_COMPOSE_FILE_PATH + "reference", DOCKER_COMPOSE_FILE_PATH + data["name"""])

    file = open(DOCKER_COMPOSE_FILE_PATH + data["name"] + "/docker-compose.yml", "r")
    text = file.read()
    file.close()

    text = text.replace("\"NODE START COMMAND\"",
                        "\"tezos-node --cors-header='content-type' --cors-origin='*' --history-mode {history_mode} --network {network} --rpc-addr 0.0.0.0:8732\""
                        .format(
                            history_mode=data["history_mode"],
                            network=data["network"]
                        )
                        )
    text = text.replace("\"TEZOS NETWORK\"",
                        "\"{}\"".format(data["network"])
                        )
    text = text.replace("image: arronax",
                        "image: arronax-{}".format(data["network"])
                        )
    text = text.replace("\"3080:80\"",
                        "\"{}:80\"".format(data["arronax_port"])
                        )
    text = text.replace("\"4080:80\"",
                        "\"{}:80\"".format(data["conseil_port"])
                        )
    text = text.replace("\"8732:8732\"",
                        "\"{}:8732\"".format(data["node_port"])
                        )

    file = open(DOCKER_COMPOSE_FILE_PATH + data["name"] + "/docker-compose.yml", "w")
    file.write(text)
    file.close()

    os.system(SCRIPT_FILE_PATH +
              "start_node.sh" +
              " " +
              data["name"]
              )

    update_status(data["name"], "running")


def stop_node(name):
    os.system(SCRIPT_FILE_PATH +
              "stop_node.sh " +
              name
              )


def delete_node(name):
    os.system(SCRIPT_FILE_PATH +
              "delete_node.sh " +
              name
              )
    shutil.rmtree(DOCKER_COMPOSE_FILE_PATH + name)


def restart_node(name):
    os.system(SCRIPT_FILE_PATH +
              "restart_node.sh " +
              name
              )