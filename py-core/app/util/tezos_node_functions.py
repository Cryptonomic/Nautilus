import wget
import tarfile
import os
import shutil
import logging
import docker

from util.app_functions import *

SCRIPT_FILE_PATH = "./util/scripts/"
DOCKER_COMPOSE_FILE_PATH = "util/docker-compose/"
LOGGING_FILE_PATH = "./logs/logs.txt"

LOGGING_FORMAT = "<<%(levelname)s>> %(asctime)s | %(message)s"

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

logging.basicConfig(filename=LOGGING_FILE_PATH,
                    format=LOGGING_FORMAT,
                    level=logging.DEBUG)


def create_node(data):

    data_location = DOCKER_COMPOSE_FILE_PATH + data["name"]
    filename = ""

    # Start Node
    if data["restore"]:
        filename = download_node_snapshot(data)
        load_snapshot_data(data, filename)

    create_new_node_directory(data)

    parse_node_docker_compose_file(data)

    os.system(SCRIPT_FILE_PATH +
              "start_node.sh" +
              " " +
              data["name"]
              )

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
    if data["network"] != "dalphanet":
        if data["arronax_port"] == 0:
            file_text = file_text.replace(
                """
arronax:
  image: arronax
  restart: always
  ports:
    - "3080:80"
  networks:
    - tezos
  logging:
    driver: "json-file" 
                """, "")
        if data["conseil_port"] == 0:
            file_text = file_text.replace(
                """
conseil-postgres:
  image: postgres:11.6
  restart: always
  environment:
    POSTRGES_PASSWORD: "password"
    POSTGRES_USER: "conseil"
    POSTGRES_DB: "conseil"
    POSTGRES_INITDB_ARGS: "--lc-collate=en_US.UTF-8 -E UTF8"
  expose:
    - 5423
  networks:
    - tezos
  volumes:
    - ../../data/conseil.sql:/docker-entrypoint-initdb.d/conseil.sql
  logging:
    driver: "json-file"

conseil-lorre:
  image: cryptonomictech/conseil:latest
  restart: always
  environment:
    DB_Host: "conseil-postgres"
    DB_Port : 5432
    DB_User: "conseil"
    DB_Password: "password"
    DB_Database: "conseil"
    XTZ_Host: "tezos-node"
    XTZ_Port: 8732
    XTZ_Network": "TEZOS NETWORK"
  command: "conseil-lorre"
  networks:
    - tezos
  logging:
    driver: "json-file"

conseil-api:
  image: cryptonomictech/conseil:latest
  restart: always
  environment:
    DB_Host: "conseil-postgres"
    DB_Port: 5432
    DB_User: "conseil"
    DB_Password: "password"
    DB_Database: "conseil"
    XTZ_Host: "tezos-node"
    XTZ_Port: 8732
    XTZ_Network: "TEZOS NETWORK"
  command: "conseil-api"
  ports:
    - "4080:80"
  expose:
    - 80
  networks:
    - tezos
  logging:
    driver: "json-file"
            """, " ")
    return file_text


def parse_node_docker_compose_file(data):
    file = open(DOCKER_COMPOSE_FILE_PATH + data["name"] + "/docker-compose.yml", "r")
    node_docker_compose_text_file = file.read()
    file.close()

    node_docker_compose_text_file = node_docker_compose_text_file.replace("\"NODE START COMMAND\"",
                        "\"tezos-node --cors-header='content-type' --cors-origin='*' --history-mode {} --network {} --rpc-addr 0.0.0.0:8732\""
                        .format(
                            data["history_mode"],
                            data["network"]
                        )
                        )

    if data["network"] != "dalphanet":
        node_docker_compose_text_file = node_docker_compose_text_file.replace("\"TEZOS NETWORK\"",
                            "\"{}\"".format(data["network"])
                            )
        node_docker_compose_text_file = node_docker_compose_text_file.replace("image: arronax",
                            "image: arronax-{}".format(data["network"])
                            )
        node_docker_compose_text_file = node_docker_compose_text_file.replace("\"3080:80\"",
                            "\"{}:80\"".format(data["arronax_port"])
                            )
        node_docker_compose_text_file = node_docker_compose_text_file.replace("\"4080:80\"",
                            "\"{}:80\"".format(data["conseil_port"])
                            )

    node_docker_compose_text_file = node_docker_compose_text_file.replace("\"8732:8732\"",
                        "\"{}:8732\"".format(data["node_port"])
                        )

    if data["history_mode"] == "archive":
        node_docker_compose_text_file = node_docker_compose_text_file.replace("./tezos-data:/var/run/tezos",
                            "./{}:/var/run/tezos".format("tezos-node_data-dir")
                            )

    file = open(DOCKER_COMPOSE_FILE_PATH + data["name"] + "/docker-compose.yml", "w")
    file.write(node_docker_compose_text_file)
    file.close()


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


def get_container_logs(name):
    docker_client = docker.from_env()
    output = dict()
    output["conseil"] = str(docker_client.containers.get(name + "_conseil-api_1").logs(tail=100))
    output["lorre"] = str(docker_client.containers.get(name + "_conseil-lorre_1").logs(tail=100))
    output["tezos"] = str(docker_client.containers.get(name + "_tezos-node_1").logs(tail=100))
    output["arronax"] = str(docker_client.containers.get(name + "_arronax_1").logs(tail=100))
    output["postgres"] = str(docker_client.containers.get(name + "_conseil-postgres_1").logs(tail=100))
    docker_client.close()
    return output
