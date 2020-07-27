from flask import Flask, render_template, request, redirect, flash
import os
import socket
import shutil
import wget
import tarfile
import docker

from util.database_functions import *

SECRET_KEY = "driptonomic"

app = Flask(__name__)

# Path to location of shell scripts
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


def get_next_port():
    port = get_max_port() + 1
    ports = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        if ports.connect_ex(("127.0.0.1", port)) != 0:
            return port
        port += 1


@app.route("/")
def start_page():
    nodes = get_node_names()
    return render_template("index.html", nodes=nodes)


@app.route("/node_setup")
def new_node_setup():
    return render_template("node_options.html")


@app.route("/start_node", methods=['GET'])
def node_start_page():

    # Store all user args
    p_name = str(request.args.get("name"))
    p_snapshot_restore = request.args.get("restore")
    p_network = str(request.args.get("network"))
    p_history_mode = str(request.args.get("mode"))

    if is_name_taken(p_name):
        flash("The name you have provided is already being used.", "error")
        return render_template("node_options.html")

    # Store data for this network
    data = dict()
    data["name"] = p_name
    data["arronax_port"] = get_next_port()
    data["network"] = p_network
    data["history_mode"] = p_history_mode
    data["status"] = "starting"

    data_location = DOCKER_COMPOSE_FILE_PATH + p_name
    filename = ""

    # Start Node
    if p_snapshot_restore:
        shutil.copytree(DOCKER_COMPOSE_FILE_PATH + "reference-snapshot", DOCKER_COMPOSE_FILE_PATH + p_name)

        if p_network == "mainnet" and p_history_mode == "archive":
            filename = wget.download(MAINNET_DATA_DIR, data_location)

        if p_network == "mainnet" and p_history_mode == "full":
            filename = wget.download(MAINNET_FULL_SNAPSHOT, data_location)

        if p_network == "mainnet" and p_history_mode == "rolling":
            filename = wget.download(MAINNET_ROLLING_SNAPSHOT, data_location)

        if p_network == "carthagenet" and p_history_mode == "archive":
            filename = wget.download(CARTHAGENET_DATA_DIR, data_location)

        if p_network == "carthagenet" and p_history_mode == "full":
            filename = wget.download(CARTHAGENET_FULL_SNAPSHOT, data_location)

        if p_network == "carthagenet" and p_history_mode == "rolling":
            filename = wget.download(CARTHAGENET_ROLLING_SNAPSHOT, data_location)

        if p_history_mode == "archive":
            file = tarfile.open(data_location + "/tezos-data.tar.gz")
            file.extractall(data_location)
            file.close()
            os.remove(data_location + "/tezos-data.tar.gz")
        else:
            docker_volumes = dict()

            docker_volumes[os.getcwd() + DOCKER_COMPOSE_FILE_PATH + p_name + "/tezos-data"] = dict()
            docker_volumes[os.getcwd() + DOCKER_COMPOSE_FILE_PATH + p_name + "/tezos-data"]["bind"] = "/var/run/tezos"
            docker_volumes[os.getcwd() + DOCKER_COMPOSE_FILE_PATH + p_name + "/tezos-data"]["mode"] = "rw"

            docker_volumes[os.getcwd() + DOCKER_COMPOSE_FILE_PATH + p_name + "/" + filename] = dict()
            docker_volumes[os.getcwd() + DOCKER_COMPOSE_FILE_PATH + p_name + "/" + filename]["bind"] = "/snapshot"
            docker_volumes[os.getcwd() + DOCKER_COMPOSE_FILE_PATH + p_name + "/" + filename]["mode"] = "rw"

            docker_client = docker.from_env()
            docker_client.containers.run("tezos/tezos:latest-release",
                                         "tezos-snapshot-import",
                                         auto_remove=True,
                                         volumes=docker_volumes
                                         )
    else:
        shutil.copytree(DOCKER_COMPOSE_FILE_PATH + "reference", DOCKER_COMPOSE_FILE_PATH + p_name)

    file = open(DOCKER_COMPOSE_FILE_PATH + p_name + "/docker-compose.yml", "r")
    text = file.read()
    file.close()

    text = text.replace("\"NODE START COMMAND\"",
                        "\"tezos-node --cors-header='content-type' --cors-origin='*' --history-mode {history_mode} --network {network} --rpc-addr 0.0.0.0:8732\""
                        .format(
                            history_mode=p_history_mode,
                            network=p_network
                            )
                        )
    text = text.replace("\"TEZOS NETWORK\"",
                        "\"{}\"".format(p_network)
                        )
    text = text.replace("\"3080:80\"",
                        "\"{}:80\"".format(data["arronax_port"])
                        )

    file = open(DOCKER_COMPOSE_FILE_PATH + p_name + "/docker-compose.yml", "w")
    file.write(text)
    file.close()

    os.system(SCRIPT_FILE_PATH +
              "start_node.sh" +
              " " +
              p_name
              )

    # Store node process statistics
    data["status"] = "running"

    add_node(data)

    return redirect("/")


@app.route("/stop_node", methods=["GET"])
def stop_node():
    p_name = request.args.get('name')
    os.system(SCRIPT_FILE_PATH +
              "stop_node.sh " +
              p_name
              )
    update_status(p_name, "stopped")
    return render_template("node.html", node=get_node_data(p_name))


@app.route("/restart_node", methods=['GET'])
def restart_node():
    p_name = str(request.args.get("name"))

    os.system(SCRIPT_FILE_PATH +
              "restart_node.sh " +
              p_name
              )

    update_status(p_name, "running")
    return redirect("/node?name=" + p_name)


@app.route("/delete_node", methods=['GET'])
def delete_node():
    name = str(request.args.get("name"))

    os.system(SCRIPT_FILE_PATH +
              "delete_node.sh " +
              name
              )

    remove_node(name)
    return redirect("/")


@app.route("/node", methods=["GET"])
def node_page():
    p_name = request.args.get("name")
    data = get_node_data(p_name)
    return render_template("node.html", node=data)


@app.route("/rpc", methods=['GET'])
def node_rpc_page():
    p_name = request.args.get("name")
    data = get_node_data(p_name)
    return render_template("rpc.html", node=data)


if __name__ == "__main__":
    setup_database()
    app.debug = True
    app.config['SECRET_KEY'] = SECRET_KEY
    app.run()
