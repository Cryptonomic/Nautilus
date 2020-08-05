import socket

from util.database_functions import *


STARTING_PORT_LOCATION = 50000


def get_next_port(num_ports):
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
