import yaml

from util.database_functions import *

CONSEIL_API_TEXT = \
    """
    image: cryptonomictech/conseil:latest
    restart: always
    environment:
      CONSEIL_API_DB_URL: "jdbc:postgresql://conseil-postgres:5432/conseil"
      CONSEIL_API_DB_USER: "conseil"
      CONSEIL_API_DB_PASSWORD: "password"
      CONSEIL_API_DB_NAME: "conseil"
      CONSEIL_LORRE_DB_URL: "jdbc:postgresql://conseil-postgres:5432/conseil"
      CONSEIL_LORRE_DB_USER: "conseil"
      CONSEIL_LORRE_DB_PASSWORD: "password"
      CONSEIL_LORRE_DB_NAME: "conseil"
      CONSEIL_XTZ_NODE_HOSTNAME: "tezos-node"
      CONSEIL_XTZ_NODE_PORT: 8732
      CONSEIL_XTZ_NETWORK: "TEZOS NETWORK"
      CONSEIL_XTZ_ENABLED: "true"
      JVM_XMX: "4G"
      CONSEIL_API_KEY: "conseil"
      CONSEIL_XTZ_NODE_PATH_PREFIX: "TEZOS PREFIX"
    command: "conseil-api"
    ports:
      - "4080:80"
    expose:
      - 80
    logging:
      driver: "json-file"
    """

LORRE_TEXT = \
    """
    image: cryptonomictech/conseil:latest
    restart: always
    environment:
      CONSEIL_API_DB_URL: "jdbc:postgresql://conseil-postgres:5432/conseil"
      CONSEIL_API_DB_USER: "conseil"
      CONSEIL_API_DB_PASSWORD: "password"
      CONSEIL_API_DB_NAME: "conseil"
      CONSEIL_LORRE_DB_URL: "jdbc:postgresql://conseil-postgres:5432/conseil"
      CONSEIL_LORRE_DB_USER: "conseil"
      CONSEIL_LORRE_DB_PASSWORD: "password"
      CONSEIL_LORRE_DB_NAME: "conseil"
      CONSEIL_XTZ_ENABLED: "true"
      CONSEIL_XTZ_NODE_PROTOCOL: "http"
      CONSEIL_XTZ_NODE_HOSTNAME: "tezos-node"
      CONSEIL_XTZ_NODE_PORT: 8732
      CONSEIL_XTZ_NETWORK: "TEZOS NETWORK"
      LORRE_RUNNER_PLATFORM: "tezos"
      LORRE_RUNNER_NETWORK: "TEZOS NETWORK"
      CONSEIL_XTZ_NODE_PATH_PREFIX: "TEZOS PREFIX"
      JVM_XMX: "4G"
      CONSEIL_API_KEY: "conseil"
    command: "conseil-lorre"
    logging:
      driver: "json-file"
    """

POSTGRES_TEXT = \
    """
    image: postgres:11.6
    restart: always
    environment:
      POSTRGES_PASSWORD: "password"
      POSTGRES_USER: "conseil"
      POSTGRES_DB: "conseil"
      POSTGRES_INITDB_ARGS: "--lc-collate=en_US.UTF-8 -E UTF8"
    expose:
      - 5423
    volumes:
      - ../../data/conseil.sql:/docker-entrypoint-initdb.d/conseil.sql
    logging:
      driver: "json-file"
    """

ARRONAX_TEXT = \
    """
    image: arronax
    restart: always
    ports:
      - "3080:80"
    logging:
      driver: "json-file"
    """

TEZOS_NODE_TEXT = \
    """
    image: tezos/tezos:latest-release
    restart: always
    ports:
      - "8732:8732"
    expose:
      - 8732
    command: "NODE START COMMAND"
    logging:
      driver: "json-file"
    """


def get_conseil_docker_compose():
    return yaml.load(CONSEIL_API_TEXT, Loader=yaml.BaseLoader)


def get_lorre_docker_compose():
    return yaml.load(LORRE_TEXT, Loader=yaml.BaseLoader)


def get_postgres_docker_compose():
    return yaml.load(POSTGRES_TEXT, Loader=yaml.BaseLoader)


def get_arronax_docker_compose():
    return yaml.load(ARRONAX_TEXT, Loader=yaml.BaseLoader)


def get_tezos_node_docker_compose():
    return yaml.load(TEZOS_NODE_TEXT, Loader=yaml.BaseLoader)


def get_snapshot_tezos_node_docker_compose():
    output = get_tezos_node_docker_compose()
    output["volumes"] = "./tezos-data:/var/run/tezos"
    return output


def build_docker_compose_file(data):
    yaml_object = dict()
    yaml_object["version"] = '3'
    yaml_object["services"] = {}

    if data["restore"]:
        yaml_object["services"]["tezos-node"] = get_snapshot_tezos_node_docker_compose()
        if data["history_mode"] == "archive":
            yaml_object["services"]["tezos-node"]["volumes"] = ["./{}:/var/run/tezos".format("tezos-node_data-dir")]
    else:
        yaml_object["services"]["tezos-node"] = get_tezos_node_docker_compose()

    if data["network"] == "ebetanet":
        yaml_object["services"]["tezos-node"]["image"] = "tezos/tezos:ebetanet-release"

    yaml_object["services"]["tezos-node"]["command"] = \
        "tezos-node --cors-header='content-type' --cors-origin='*' --history-mode {} --network {} --rpc-addr 0.0.0.0:8732".format(
            data["history_mode"],
            data["network"]
        )

    yaml_object["services"]["tezos-node"]["ports"] = ["{}:8732".format(data["node_port"])]

    if data["conseil_port"] != 0:
        yaml_object["services"]["conseil-api"] = get_conseil_docker_compose()
        yaml_object["services"]["conseil-lorre"] = get_lorre_docker_compose()
        yaml_object["services"]["conseil-postgres"] = get_postgres_docker_compose()

        yaml_object["services"]["conseil-lorre"]["environment"]["CONSEIL_XTZ_NETWORK"] = data["network"]
        yaml_object["services"]["conseil-lorre"]["environment"]["LORRE_RUNNER_NETWORK"] = data["network"]
        yaml_object["services"]["conseil-lorre"]["environment"]["CONSEIL_XTZ_NODE_PATH_PREFIX"] = ""
        yaml_object["services"]["conseil-api"]["environment"]["CONSEIL_XTZ_NETWORK"] = data["network"]
        yaml_object["services"]["conseil-api"]["ports"] = ["{}:1337".format(data["conseil_port"])]
        yaml_object["services"]["conseil-api"]["environment"]["CONSEIL_XTZ_NODE_PATH_PREFIX"] = ""

        yaml_object["services"]["conseil-api"]["image"] = "cryptonomictech/conseil:{}".format(data["conseil_branch"])
        yaml_object["services"]["conseil-lorre"]["image"] = "cryptonomictech/conseil:{}".format(data["conseil_branch"])

    if data["arronax_port"] != 0:
        yaml_object["services"]["arronax"] = get_arronax_docker_compose()

        yaml_object["services"]["arronax"]["image"] = "arronax-{}".format(data["network"])
        yaml_object["services"]["arronax"]["ports"] = ["{}:80".format(data["arronax_port"])]

    return yaml.dump(yaml_object)


def remove_conseil_from_file(file):
    yaml_object = yaml.load(file.read(), Loader=yaml.BaseLoader) or {}

    yaml_object["services"].pop("conseil-api")
    yaml_object["services"].pop("conseil-lorre")
    yaml_object["services"].pop("conseil-postgres")

    file.write(yaml.dump(yaml_object))


def add_conseil_to_file(file, name, branch):
    yaml_object = dict(yaml.load(file.read(), Loader=yaml.BaseLoader)) or {}

    data = get_node_data(name)

    yaml_object["services"]["conseil-api"] = get_conseil_docker_compose()
    yaml_object["services"]["conseil-lorre"] = get_lorre_docker_compose()
    yaml_object["services"]["conseil-postgres"] = get_postgres_docker_compose()

    yaml_object["services"]["conseil-lorre"]["environment"]["CONSEIL_XTZ_NETWORK"] = data["network"]
    yaml_object["services"]["conseil-lorre"]["environment"]["LORRE_RUNNER_NETWORK"] = data["network"]
    yaml_object["services"]["conseil-lorre"]["environment"]["CONSEIL_XTZ_NODE_PATH_PREFIX"] = ""
    yaml_object["services"]["conseil-api"]["environment"]["CONSEIL_XTZ_NETWORK"] = data["network"]
    yaml_object["services"]["conseil-api"]["ports"] = ["{}:1337".format(data["conseil_port"])]
    yaml_object["services"]["conseil-api"]["environment"]["CONSEIL_XTZ_NODE_PATH_PREFIX"] = ""

    yaml_object["services"]["conseil-api"]["image"] = "cryptonomictech/conseil:{}".format(branch)
    yaml_object["services"]["conseil-lorre"]["image"] = "cryptonomictech/conseil:{}".format(branch)

    file.write(yaml.dump(yaml_object))