from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
import os
import psutil
import time
from util.database_functions import *

SECRET_KEY = "driptonomic"
app = Flask(__name__)

# Counter for ports to use when starting new nodes
port_counter = 50000
# List of nodes running
nodes = list()
# Path to location of shell scripts
SCRIPT_FILE_PATH = "./util/scripts/"
LOGGING_FILE_PATH = "util/tezos-nodes/data"


def pid_stats(pid):
    process = psutil.Process(pid)
    data = dict()
    data['status'] = process.status()
    data['runtime'] = time.time() - process.create_time()
    return data


def get_logs(name):
    os.system(f'docker logs tezos-node-{name} > {LOGGING_FILE_PATH}/{name}/{name}.tzlog')
    logfile = open(f'{LOGGING_FILE_PATH}/{name}/{name}.tzlog')
    output = logfile.read()
    logfile.close()
    response = jsonify(status="success", logs=output)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/logs/', methods=['GET'])
def log_viewer():
    return get_logs(request.args.get('name'))


@app.route("/")
def start_page():
    return render_template("index.html", nodes=nodes)


@app.route("/node_setup")
def new_node_setup():
    return render_template("node_options.html")


@app.route("/start_node", methods=['GET'])
def node_start_page():

    # Store the name of this new node
    name = request.args.get("name")
    if name in nodes:
        flash("The name you have provided is already being used.", "error")
        return render_template("node_options.html")

    # Store data for this network
    global port_counter
    data = dict()
    print(port_counter)
    data["name"] = str(name)
    data["rpc_port"] = port_counter
    data["exposition_port"] = port_counter + 1
    data["conseil_port"] = port_counter + 2
    data["arronax_port"] = port_counter + 3
    data["postgres_port"] = port_counter + 4
    data["network"] = str(request.args.get("network"))
    data["history_mode"] = str(request.args.get("mode"))
    data["status"] = "starting"
    port_counter += 5

    # Create file for storing logs
    os.system(f'touch ${LOGGING_FILE_PATH + name}.tzlog')

    # Start Node
    if request.args.get("restore"):

        os.system(SCRIPT_FILE_PATH +
                  "start_node_snapshot.sh " +
                  request.args.get("network") +
                  " " +
                  str(data["rpc_port"]) +
                  " " +
                  str(data["exposition_port"]) +
                  " " +
                  name +
                  " " +
                  str(data["history_mode"])
                  )
    else:
        os.system(SCRIPT_FILE_PATH +
                  "start_node.sh " +
                  request.args.get("network") +
                  " " +
                  str(data["rpc_port"]) +
                  " " +
                  str(data["exposition_port"]) +
                  " " +
                  name +
                  " " +
                  str(data["history_mode"])
                  )

    os.system(SCRIPT_FILE_PATH +
              "setup_conseil.sh " +
              name +
              " " +
              str(data["postgres_port"])
              )

    os.system(SCRIPT_FILE_PATH +
              "setup_arronax.sh " +
              name +
              " " +
              str(data["arronax_port"]) +
              " " +
              str(data["network"]) +
              " " +
              str(data["conseil_port"]) +
              " " +
              str(data["rpc_port"])
              )

    os.system(SCRIPT_FILE_PATH +
              "run_conseil.sh " +
              name +
              " " +
              str(data["rpc_port"]) +
              " " +
              str(data["network"]) +
              " " +
              str(data["conseil_port"]) +
              " " +
              str(data["postgres_port"])
              )

    os.system(SCRIPT_FILE_PATH +
              "run_arronax.sh " +
              name
              )

    # Store node process statistics
    data["status"] = "running"

    nodes.append(str(name))

    add_node(data)

    return redirect("/")


@app.route("/stop_node", methods=["GET"])
def stop_node():

    os.system(SCRIPT_FILE_PATH +
              "stop_node.sh " +
              request.args.get('name')
              )

    os.system(SCRIPT_FILE_PATH +
              "stop_conseil.sh " +
              request.args.get('name')
              )

    os.system(SCRIPT_FILE_PATH +
              "stop_arronax.sh " +
              request.args.get('name')
              )

    os.system(SCRIPT_FILE_PATH +
              "stop_postgres.sh " +
              request.args.get('name')
              )

    update_status(request.args.get('name'), "stopped")
    return render_template("node.html", node=get_node_data(request.args.get("name")))


@app.route("/restart_node", methods=['GET'])
def restart_node():
    name = str(request.args.get("name"))
    data = get_node_data(name)

    os.system(SCRIPT_FILE_PATH +
              "restart_node.sh " +
              str(data["network"]) +
              " " +
              str(data["rpc_port"]) +
              " " +
              str(data["exposition_port"]) +
              " " +
              str(name) +
              " " +
              str(data["history_mode"])
              )

    os.system(SCRIPT_FILE_PATH +
              "restart_conseil.sh " +
              name +
              " " +
              str(data["rpc_port"]) +
              " " +
              str(data["network"]) +
              " " +
              str(data["conseil_port"])
              )

    os.system(SCRIPT_FILE_PATH +
              "restart_arronax.sh " +
              name
              )

    update_status(name, "running")
    return redirect("/node?name=" + name)


@app.route("/delete_node", methods=['GET'])
def delete_node():
    name = str(request.args.get("name"))
    os.system(SCRIPT_FILE_PATH + "delete_node.sh " + name)
    remove_node(name)
    nodes.remove(name)
    return redirect("/")


@app.route("/node", methods=["GET"])
def node_page():
    return render_template("node.html", node=get_node_data(request.args.get("name")))


@app.route("/rpc", methods=['GET'])
def node_rpc_page():
    return render_template("rpc.html", node=get_node_data(request.args.get("name")))


if __name__ == "__main__":
    setup_database()
    nodes = list(map(lambda node: node[0], get_all_nodes()))
    port_counter = get_max_port()
    print(port_counter)
    app.debug = True
    app.config['SECRET_KEY'] = SECRET_KEY
    app.run()
