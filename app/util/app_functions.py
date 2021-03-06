import os
import socket
import docker
import logging
from conseil import conseil

from util.database_functions import *
from util.tezos_node_functions import get_container_logs, stop_node, restart_node, delete_node, update_status

STARTING_PORT_LOCATION = 50000

LOGGING_FILE_PATH = "./logs/logs.txt"
LOGGING_FORMAT = "<<%(levelname)s>> %(asctime)s | %(message)s"
logging.basicConfig(filename=LOGGING_FILE_PATH,
                    format=LOGGING_FORMAT,
                    level=logging.DEBUG)


def get_next_port(num_ports: int):
    output = list()
    port = get_max_node_port()
    if port is None:
        port = STARTING_PORT_LOCATION
    ports = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for x in range(num_ports):
        port_not_found = True
        while port_not_found:
            if ports.connect_ex(("127.0.0.1", port)) != 0:
                output.append(port)
                port_not_found = False
            port += 1
    return output


def setup_job_queue_server(password: str):
    try:
        ports = dict()
        ports["6379"] = "6379"
        docker_client = docker.from_env()
        docker_client.containers.run("redis",
                                     "redis-server --requirepass " + password,
                                     auto_remove=True,
                                     detach=True,
                                     ports=ports,
                                     name="nautilus-core-redis"
                                     )
    except docker.errors.APIError as e:
        log_fatal_error(e, "Could not start Redis server on Docker.")
        exit(1)


def get_latest_block_level(network: str):
    if network == "mainnet":
        return conseil.tezos.mainnet.blocks.head
    return conseil.tezos.carthagenet.blocks.head


def parse_logs(name: str):
    logs = get_container_logs(name)["tezos"]
    log_lines = logs.splitlines()
    block_level = 0
    network = get_network(name)
    for line in log_lines:
        words = line.split(" ")

        # Check if still bootstrapping
        if get_status(name) == "bootstrapping":
            if "validator.chain: Update current head to" in line and "level" in line:
                level = words[words.index("(level") + 1].replace(",", "")
                if int(level) > block_level:
                    block_level = int(level)

    if int(block_level) < get_latest_block_level(network):
        update_status(name, "bootstrapping")
    else:
        update_status(name, "running")


def update_node_status():
    for node in get_node_names():
        parse_logs(node)


def update_node_status(name):
    docker_client = None
    try:
        docker_client = docker.from_env()
    except Exception as e:
        log_fatal_error(e, "Unable to get Docker Environment")
        return
    try:
        container = docker_client.containers.get("{}_tezos-node_1".format(name))
        if get_status(name) != container.status:
            if container.status == "exited":
                stop_node(name)
            if container.status == "running":
                restart_node(name)
            update_status(name, "stopped" if container.status == "exited" else container.status)
    except docker.errors.NotFound as e:
        log_fatal_error(e, "This node's container has been removed.")
        remove_node(name)


def validate_node_name(name: str):
    return name\
        .lower()\
        .replace("-", "_")\
        .replace(" ", "_")


def log_fatal_error(exception, message):
    logging.error("""
     /\  ___\ /\  __ \   /\__  _\ /\  __ \   /\ \          /\  ___\   /\  == \   /\  == \   /\  __ \   /\  == \   
     \ \  __\ \ \  __ \  \/_/\ \/ \ \  __ \  \ \ \____     \ \  __\   \ \  __<   \ \  __<   \ \ \/\ \  \ \  __<   
      \ \_\    \ \_\ \_\    \ \_\  \ \_\ \_\  \ \_____\     \ \_____\  \ \_\ \_\  \ \_\ \_\  \ \_____\  \ \_\ \_\ 
       \/_/     \/_/\/_/     \/_/   \/_/\/_/   \/_____/      \/_____/   \/_/ /_/   \/_/ /_/   \/_____/   \/_/ /_/ 
    """)
    logging.error(message)
    logging.error(exception)


