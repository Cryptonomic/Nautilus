import wget
import tarfile
import os
import shutil
import logging
import docker
import requests
import yaml

from .app_functions import *
from .docker_compose_utils import *

SCRIPT_FILE_PATH = "./app/util/scripts/"
DOCKER_COMPOSE_FILE_PATH = os.path.expanduser("~/.nautilus-core/")

# TODO: CHANGE THESE LINKS
# Snapshot Download URLs
MAINNET_FULL_SNAPSHOT = "https://conseil-snapshots.s3.amazonaws.com/tezos-node_snapshot-latest.full"
MAINNET_ROLLING_SNAPSHOT = "https://conseil-snapshots.s3.amazonaws.com/tezos-node_snapshot-latest.full"
CARTHAGENET_FULL_SNAPSHOT = "https://conseil-snapshots.s3.amazonaws.com/tezos-node_snapshot-latest.full"
CARTHAGENET_ROLLING_SNAPSHOT = "https://conseil-snapshots.s3.amazonaws.com/tezos-node_snapshot-latest.full"
DELPHINET_FULL_SNAPSHOT = "https://conseil-snapshots.s3.amazonaws.com/tezos-node_snapshot-latest.full"
DELPHINET_ROLLING_SNAPSHOT = "https://conseil-snapshots.s3.amazonaws.com/tezos-node_snapshot-latest.full"

# Data-Directory Download URLs
MAINNET_DATA_DIR = "https://conseil-snapshots.s3.amazonaws.com/tezos-node_data-dir.tar.gz"
CARTHAGENET_DATA_DIR = "https://conseil-snapshots.s3.amazonaws.com/tezos-data.tar.gz"
DELPHINET_DATA_DIR = ""


LOGGING_FILE_PATH = "./app/logs/logs.txt"
LOGGING_FORMAT = "<<%(levelname)s>> %(asctime)s | %(message)s"
logging.basicConfig(filename=LOGGING_FILE_PATH,
                    format=LOGGING_FORMAT,
                    level=logging.DEBUG)


def create_node(data):

    try:
        text = build_docker_compose_file(data)
    except Exception as e:
        log_fatal_error(e, "Could not build docker compose file.")
        delete_node(data["name"])
        return

    try:
        create_new_node_directory(data["name"], text)
    except Exception as e:
        log_fatal_error(e, "Could not create node directory.")
        delete_node(data["name"])
        return

    try:
        if data["restore"]:
            filename = download_node_snapshot(data)
            load_snapshot_data(data, filename)
    except Exception as e:
        log_fatal_error(e, "Could not download snapshot. Continuing without snapshot restore.")

    try:
        os.system(SCRIPT_FILE_PATH +
                  "start_node.sh" +
                  " " +
                  data["name"]
                  )
    except Exception as e:
        log_fatal_error(e, "Could not run script to start node.")
        delete_node(data["name"])
        return

    update_status(data["name"], "bootstrapping")


def download_node_snapshot(data):
    data_location = DOCKER_COMPOSE_FILE_PATH + data["name"]
    filename = ""

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

    if data["network"] == "delphinet" and data["history_mode"] == "archive":
        filename = wget.download(DELPHINET_DATA_DIR, data_location)

    if data["network"] == "delphinet" and data["history_mode"] == "full":
        filename = wget.download(DELPHINET_FULL_SNAPSHOT, data_location)

    if data["network"] == "delphinet" and data["history_mode"] == "rolling":
        filename = wget.download(DELPHINET_ROLLING_SNAPSHOT, data_location)

    return filename


def load_snapshot_data(data, filename):
    data_location = DOCKER_COMPOSE_FILE_PATH + data["name"]

    if data["history_mode"] == "archive":
        file = tarfile.open(filename)
        file.extractall(data_location)
        file.close()
        os.remove(filename)
        # os.remove(data_location + "/tezos-data/node/data/identity.json")
    else:
        docker_volumes = dict()
        docker_data_path = os.getcwd() + "/" + DOCKER_COMPOSE_FILE_PATH + data["name"] + "/tezos-data"
        docker_snapshot_path = os.getcwd() + "/" + filename

        docker_volumes[docker_data_path] = dict()
        docker_volumes[docker_data_path]["bind"] = "/var/run/tezos"
        docker_volumes[docker_data_path]["mode"] = "rw"

        docker_volumes[docker_snapshot_path] = dict()
        docker_volumes[docker_snapshot_path]["bind"] = "/snapshot"
        docker_volumes[docker_snapshot_path]["mode"] = "rw"

        docker_client = docker.from_env()
        docker_client.containers.run("tezos/tezos:latest-release",
                                     "tezos-snapshot-import",
                                     auto_remove=True,
                                     volumes=docker_volumes
                                     )


def create_new_node_directory(name, contents):
    os.mkdir(DOCKER_COMPOSE_FILE_PATH + name)

    wget.download(url="https://raw.githubusercontent.com/Cryptonomic/Conseil/master/sql/conseil.sql",
                  out=DOCKER_COMPOSE_FILE_PATH + name)

    file = open(DOCKER_COMPOSE_FILE_PATH + name + "/docker-compose.yml", "w+")
    file.write(contents)
    file.close()


def stop_node(name):
    try:
        os.system(SCRIPT_FILE_PATH +
                  "stop_node.sh " +
                  name
                  )
    except Exception as e:
        log_fatal_error(e, "Unable to stop node.")


def delete_node(name):
    try:
        os.system(SCRIPT_FILE_PATH +
                  "delete_node.sh " +
                  name
                  )
        shutil.rmtree(DOCKER_COMPOSE_FILE_PATH + name)
    except Exception as e:
        log_fatal_error(e, "Unable to delete node.")


def restart_node(name):
    try:
        os.system(SCRIPT_FILE_PATH +
                  "restart_node.sh " +
                  name
                  )
    except Exception as e:
        log_fatal_error(e, "Unable to restart node.")


def get_container_logs(data):
    try:
        docker_client = docker.from_env()
        output = dict()
        name = data["name"]
    except Exception as e:
        log_fatal_error(e, "Unable to get Docker Environment")

    try:
        output["conseil"] = str(docker_client.containers.get(name + "_conseil-api_1").logs(tail=100))
        output["postgres"] = str(docker_client.containers.get(name + "_conseil-postgres_1").logs(tail=100))
        output["lorre"] = str(docker_client.containers.get(name + "_conseil-lorre_1").logs(tail=100))
    except:
        output["conseil"] = "Loading Logs..."
        output["postgres"] = "Loading Logs..."
        output["lorre"] = "Loading Logs..."

    try:
        output["arronax"] = str(docker_client.containers.get(name + "_arronax_1").logs(tail=100))
    except:
        output["arronax"] = "Loading Logs..."

    try:
        output["tezos"] = str(docker_client.containers.get(name + "_tezos-node_1").logs(tail=100))
    except:
        output["tezos"] = "Loading Logs..."

    docker_client.close()
    return output
