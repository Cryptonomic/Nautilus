from flask import Flask, render_template, request, redirect, flash
# import rq

from util.tezos_node_functions import *

SECRET_KEY = "driptonomic"

app = Flask(__name__)

# Path to location of shell scripts
SCRIPT_FILE_PATH = "./util/scripts/"
DOCKER_COMPOSE_FILE_PATH = "util/docker-compose/"


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

    if is_name_taken(p_name):
        flash("The name you have provided is already being used.", "error")
        return render_template("node_options.html")

    create_node(data)

    return redirect("/")


@app.route("/stop_node", methods=["GET"])
def stop_node():
    p_name = str(request.args.get('name'))
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
    p_name = str(request.args.get("name"))
    os.system(SCRIPT_FILE_PATH +
              "delete_node.sh " +
              p_name
              )
    shutil.rmtree(DOCKER_COMPOSE_FILE_PATH + p_name)
    remove_node(p_name)
    return redirect("/")


@app.route("/node", methods=["GET"])
def node_page():
    p_name = str(request.args.get("name"))
    data = get_node_data(p_name)
    return render_template("node.html", node=data)


@app.route("/rpc", methods=['GET'])
def node_rpc_page():
    p_name = str(request.args.get("name"))
    data = get_node_data(p_name)
    return render_template("rpc.html", node=data)


if __name__ == "__main__":
    setup_database()
    app.debug = True
    app.config['SECRET_KEY'] = SECRET_KEY
    app.run()
