from flask import Flask, render_template, request, redirect, flash, jsonify
import rq
import os
import logging
import psutil
import json

from worker import conn
from util.app_functions import *
import util.tezos_node_functions as node_functions
import util.database_functions as db

SECRET_KEY = os.urandom(32)

app = Flask(__name__)
job_queue = rq.Queue(connection=conn)

# Paths for various files
SCRIPT_FILE_PATH = "./util/scripts/"
DOCKER_COMPOSE_FILE_PATH = "util/docker-compose/"
LOGGING_FILE_PATH = "./logs/logs.txt"

APP_PORT = "4104"

LOGGING_FORMAT = "<<%(levelname)s>> %(asctime)s | %(message)s"

logging.basicConfig(filename=LOGGING_FILE_PATH,
                    format=LOGGING_FORMAT,
                    level=logging.DEBUG)

# Stores CPU Usage data for this instance of the app
cpu_data = []
ram_data = []


@app.route("/")
def start_page():
    logging.info("Opening start page.")

    logging.debug("Retrieving all nodes on machine from database.")
    nodes = db.get_node_names()
    logging.debug("Nodes retrieved from database.")

    logging.debug("Updating status of all nodes.")
    try:
        job_queue.enqueue_call(func=update_node_status, result_ttl=-1)
    except Exception as e:
        log_fatal_error(e, "Could not add function to Job Queue")

    return render_template("index.html", nodes=nodes)


@app.route("/node_setup")
def new_node_setup():
    logging.info("Opening node options page.")
    return render_template("node_options.html")


@app.route("/start_node", methods=['GET'])
def node_start_page():
    logging.info("Starting node from options given.")

    # Store all user args
    logging.debug("Retrieving node options.")
    p_name = str(request.args.get("name"))
    p_snapshot_restore = request.args.get("restore")
    p_network = str(request.args.get("network"))
    p_history_mode = str(request.args.get("mode"))
    logging.debug("Node options retrieved from user.")

    # Checking if there are any problems with the user input
    if p_name == "None" or p_history_mode == "None" or p_network == "None" \
            or p_name == "" or p_history_mode == "" or p_network == "":
        logging.warning("Not all form inputs filled out.")
        flash("Please fill in all of the options.", "error")
        return render_template("node_options.html")

    if db.is_name_taken(p_name):
        logging.warning("Node name already used.")
        flash("The name you have provided is already being used.", "error")
        return render_template("node_options.html")

    if p_network == "ebetanet":
        p_snapshot_restore = False

    logging.debug("Getting next available port.")
    try:
        ports = get_next_port(3)
    except Exception as e:
        log_fatal_error(e, "Could not find a new port for running the Nodes on.")
    logging.debug("Open ports retrieved.")

    data = dict()
    data["name"] = validate_node_name(p_name)
    data["arronax_port"] = ports[0]
    data["conseil_port"] = ports[1]
    data["node_port"] = ports[2]
    data["network"] = p_network
    data["history_mode"] = p_history_mode
    data["restore"] = p_snapshot_restore
    data["status"] = "starting"

    if not request.args.get("arronax"):
        data["arronax_port"] = 0

    if not request.args.get("conseil"):
        data["conseil_port"] = 0

    if data["history_mode"] != "archive":
        data["arronax_port"] = 0
        data["conseil_port"] = 0

    # Add node to database
    logging.debug("Adding node to database.")
    db.add_node(data)
    logging.debug("Node added to database.")

    logging.debug("Adding node start job to work queue.")
    try:
        job_queue.enqueue_call(func=node_functions.create_node, args=(data,), timeout=86400)
    except Exception as e:
        log_fatal_error(e, "Could not send 'create node' function to Job Queue server.")
    logging.debug("Node start job added to work queue.")

    return redirect("/")


@app.route("/stop_node", methods=["GET"])
def stop_node():
    logging.info("Stopping node.")

    logging.debug("Retrieving node name.")
    p_name = str(request.args.get('name'))
    logging.debug("Node name retrieved.")

    logging.debug("Updating node status in database.")
    db.update_status(p_name, "stopped")
    logging.debug("Node status updated.")

    logging.debug("Adding node stop job to work queue.")
    job_queue.enqueue_call(func=node_functions.stop_node, args=(p_name,), result_ttl=-1)
    logging.debug("Node stop job added to work queue.")

    return render_template("node.html", node=get_node_data(p_name))


@app.route("/restart_node", methods=['GET'])
def restart_node():
    logging.info("Restarting node.")

    logging.debug("Retrieving node name.")
    p_name = str(request.args.get("name"))
    logging.debug("Node name retrieved.")

    logging.debug("Updating node status in database.")
    db.update_status(p_name, "running")
    logging.debug("Node status updated.")

    logging.debug("Adding node restart job in work queue.")
    job_queue.enqueue_call(func=node_functions.restart_node, args=(p_name,), result_ttl=-1)
    logging.debug("Node restart job added to work queue.")

    return redirect("/node?name=" + p_name)


@app.route("/delete_node", methods=['GET'])
def delete_node():
    logging.info("Deleting Node.")

    logging.debug("Retrieving node name.")
    p_name = str(request.args.get("name"))
    logging.debug("Node name retrieved.")

    logging.debug("Removing node from database.")
    db.remove_node(p_name)
    logging.debug("Node removed.")

    logging.debug("Adding node delete job to work queue.")
    job_queue.enqueue_call(func=node_functions.delete_node, args=(p_name,), result_ttl=-1)
    logging.debug("Node delete job added to work queue.")

    return redirect("/")


@app.route("/node", methods=["GET"])
def node_page():
    logging.info("Loading node page.")

    logging.debug("Adding node update job to work queue.")
    job_queue.enqueue_call(func=update_node_status, result_ttl=-1)
    logging.debug("Node update job added to work queue.")

    logging.debug("Retrieving node name.")
    p_name = str(request.args.get("name"))
    logging.debug("Node name retrieved.")

    logging.debug("Retrieving node data from database.")
    data = db.get_node_data(p_name)
    logging.debug("Node data retrieved.")

    return render_template("node.html", node=data)


@app.route("/rpc", methods=['GET'])
def node_rpc_page():
    p_name = str(request.args.get("name"))
    data = db.get_node_data(p_name)
    return render_template("rpc.html", node=data)


@app.route("/get_logs")
def get_logs():
    name = str(request.args.get("name"))
    data = db.get_node_data(name)
    data = node_functions.get_container_logs(data)
    return jsonify(arronax=data["arronax"].replace("\\n", "&#013;"),
                   conseil=data['conseil'].replace("\\n", "&#013;"),
                   lorre=data['lorre'].replace("\\n", "&#013;"),
                   postgres=data['postgres'].replace("\\n", "&#013;"),
                   tezos=data['tezos'].replace("\\n", "&#013;")
                   )


@app.route("/get_cpu_data")
def get_cpu():
    cpu_data.append(psutil.cpu_percent())
    if len(cpu_data) > 300:
        cpu_data.pop(0)
    return jsonify(cpu=cpu_data)


@app.route("/get_ram_data")
def get_ram():
    ram_data.append(psutil.virtual_memory().percent)
    if len(ram_data) > 300:
        ram_data.pop(0)
    return jsonify(ram=ram_data)


if __name__ == "__main__":
    # Setup sqlite database with schema
    logging.debug("Setting up database.")
    db.setup_database()
    logging.debug("Database set up")
    # Setup flask app config, and run
    app.debug = True
    app.config['SECRET_KEY'] = SECRET_KEY
    app.run(port=APP_PORT)
