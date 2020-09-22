import socket
import docker
from conseil import conseil

from util.database_functions import *
from util.tezos_node_functions import get_node_logs


STARTING_PORT_LOCATION = 50000


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


def setup_job_queue_server():
    try:
        ports = dict()
        ports["6379"] = "6379"
        docker_client = docker.from_env()
        docker_client.containers.run("redis",
                                     "redis-server --requirepass conseil",
                                     auto_remove=True,
                                     detach=True,
                                     ports=ports,
                                     name="nautilus-core-redis"
                                     )
    except docker.errors.APIError as e:
        bruh = True


def get_latest_block_level(network: str):
    if network == "mainnet":
        return conseil.tezos.mainnet.blocks.head
    return conseil.tezos.carthagenet.blocks.head


def parse_logs(name: str):
    logs = get_node_logs(name)
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


def validate_node_name(name: str):
    return name\
        .lower()\
        .replace("-", "_")\
        .replace(" ", "_")


