import wget
import tarfile
import os
import shutil
import logging
import docker
import yaml

from util.app_functions import *

SCRIPT_FILE_PATH = "./util/scripts/"
DOCKER_COMPOSE_FILE_PATH = "util/docker-compose/"

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


LOGGING_FILE_PATH = "./logs/logs.txt"
LOGGING_FORMAT = "<<%(levelname)s>> %(asctime)s | %(message)s"
logging.basicConfig(filename=LOGGING_FILE_PATH,
                    format=LOGGING_FORMAT,
                    level=logging.DEBUG)


def create_node(data):

    # Start Node
    try:
        if data["restore"]:
            filename = download_node_snapshot(data)
            load_snapshot_data(data, filename)
    except Exception as e:
        log_fatal_error(e, "Could not download snapshot data. Will not load from snapshot.")

    try:
        create_new_node_directory(data)
    except Exception as e:
        log_fatal_error(e, "Could not create directory for node.")
        remove_node(data["name"])
        return

    try:
        parse_node_docker_compose_file(data)
    except Exception as e:
        log_fatal_error(e, "Error in parsing docker compose file.")
        remove_node(data["name"])
        return

    try:
        os.system(SCRIPT_FILE_PATH +
                  "start_node.sh" +
                  " " +
                  data["name"]
                  )
    except Exception as e:
        log_fatal_error(e, "Could not run script to start node.")
        remove_node(data["name"])
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


def create_new_node_directory(data):
    if data["network"] == "dalphanet":
        shutil.copytree(DOCKER_COMPOSE_FILE_PATH + "reference-dalpha", DOCKER_COMPOSE_FILE_PATH + data["name"])
    else:
        shutil.copytree(DOCKER_COMPOSE_FILE_PATH + "reference", DOCKER_COMPOSE_FILE_PATH + data["name"])


def remove_node_options(data, file_text):
    yaml_object = yaml.load(file_text, Loader=yaml.BaseLoader)
    if data["network"] != "dalphanet":

        if data["arronax_port"] == 0:
            yaml_object["services"].pop("arronax", None)

        if data["conseil_port"] == 0:
            yaml_object["services"].pop("conseil-postgres", None)
            yaml_object["services"].pop("conseil-lorre", None)
            yaml_object["services"].pop("conseil-api", None)

    return yaml.dump(yaml_object)


def parse_node_docker_compose_file(data):
    file = open(DOCKER_COMPOSE_FILE_PATH + data["name"] + "/docker-compose.yml", "r")
    node_docker_compose_text_file = file.read()
    file.close()

    yaml_object = yaml.load(node_docker_compose_text_file, Loader=yaml.BaseLoader)

    yaml_object["services"]["tezos-node"]["command"] = \
        "tezos-node --cors-header='content-type' --cors-origin='*' --history-mode {} --network {} --rpc-addr 0.0.0.0:8732".format(
                            data["history_mode"],
                            data["network"]
                        )

    if data["network"] != "dalphanet":
        yaml_object["services"]["conseil-lorre"]["environment"]["CONSEIL_XTZ_NETWORK"] = data["network"]
        
        yaml_object["services"]["conseil-lorre"]["environment"]["LORRE_RUNNER_NETWORK"] = data["network"]

        yaml_object["services"]["conseil-api"]["environment"]["CONSEIL_XTZ_NETWORK"] = data["network"]

        yaml_object["services"]["conseil-api"]["environment"]["CONSEIL_XTZ_NODE_PATH_PREFIX"] = ""

        yaml_object["services"]["conseil-lorre"]["environment"]["CONSEIL_XTZ_NODE_PATH_PREFIX"] = ""

        yaml_object["services"]["arronax"]["image"] = "arronax-{}".format(data["network"])

        yaml_object["services"]["arronax"]["ports"] = ["{}:80".format(data["arronax_port"])]

        yaml_object["services"]["conseil-api"]["ports"] = ["{}:1337".format(data["conseil_port"])]

    yaml_object["services"]["tezos-node"]["ports"] = ["{}:8732".format(data["node_port"])]

    if data["restore"] and data["history_mode"] == "archive":
        yaml_object["services"]["tezos-node"]["volumes"] = ["./{}:/var/run/tezos".format("tezos-node_data-dir")]

    node_docker_compose_text_file = yaml.dump(yaml_object)

    node_docker_compose_text_file = remove_node_options(data, node_docker_compose_text_file)

    file = open(DOCKER_COMPOSE_FILE_PATH + data["name"] + "/docker-compose.yml", "w")
    file.write(node_docker_compose_text_file)
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

    output["tezos"] = str(docker_client.containers.get(name + "_tezos-node_1").logs(tail=100))

    docker_client.close()
    return output
