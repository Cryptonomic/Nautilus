from flask import Flask, render_template, request, redirect, flash
import rq

from worker import conn
from util.app_functions import *
import util.tezos_node_functions as node_functions
import util.database_functions as db

SECRET_KEY = "driptonomic"

app = Flask(__name__)
job_queue = rq.Queue(connection=conn)

# Path to location of shell scripts
SCRIPT_FILE_PATH = "./util/scripts/"
DOCKER_COMPOSE_FILE_PATH = "util/docker-compose/"


@app.route("/")
def start_page():
    nodes = db.get_node_names()
    update_node_status()
    job_queue.enqueue_call(func=update_node_status, result_ttl=-1)
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

    ports = get_next_port(3)

    data = dict()
    data["name"] = p_name.lower().replace("-", "_")
    data["arronax_port"] = ports[0]
    data["conseil_port"] = ports[1]
    data["node_port"] = ports[2]
    data["network"] = p_network
    data["history_mode"] = p_history_mode
    data["restore"] = p_snapshot_restore
    data["status"] = "starting"

    if db.is_name_taken(p_name):
        flash("The name you have provided is already being used.", "error")
        return render_template("node_options.html")

    # Add node to database
    db.add_node(data)

    node_start_job = job_queue.enqueue_call(func=node_functions.create_node, args=(data,), timeout=86400)

    return redirect("/")


@app.route("/stop_node", methods=["GET"])
def stop_node():
    p_name = str(request.args.get('name'))
    db.update_status(p_name, "stopped")
    job_queue.enqueue_call(func=node_functions.stop_node, args=(p_name,), result_ttl=-1)
    return render_template("node.html", node=get_node_data(p_name))


@app.route("/restart_node", methods=['GET'])
def restart_node():
    p_name = str(request.args.get("name"))
    db.update_status(p_name, "running")
    job_queue.enqueue_call(func=node_functions.restart_node, args=(p_name,), result_ttl=-1)
    return redirect("/node?name=" + p_name)


@app.route("/delete_node", methods=['GET'])
def delete_node():
    p_name = str(request.args.get("name"))
    db.remove_node(p_name)
    job_queue.enqueue_call(func=node_functions.delete_node, args=(p_name,), result_ttl=-1)
    return redirect("/")


@app.route("/node", methods=["GET"])
def node_page():
    job_queue.enqueue_call(func=update_node_status, result_ttl=-1)
    p_name = str(request.args.get("name"))
    data = db.get_node_data(p_name)
    return render_template("node.html", node=data)


@app.route("/rpc", methods=['GET'])
def node_rpc_page():
    p_name = str(request.args.get("name"))
    data = db.get_node_data(p_name)
    return render_template("rpc.html", node=data)


if __name__ == "__main__":
    # Setup sqlite database with schema
    db.setup_database()
    # Setup flask app config, and run
    app.debug = True
    app.config['SECRET_KEY'] = SECRET_KEY
    app.run()
